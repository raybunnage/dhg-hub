from typing import Optional, List, Dict, Any, Tuple, Union, Literal
from core.types import JSON
from .types import TableName, ColumnName, FilterOperator, InsertResult
from asyncio import AsyncClient

from ...core.base_logging import Logger, log_method
from ...core.exceptions import (
    SupabaseConnectionError,
    SupabaseQueryError,
    SupabaseAuthenticationError,
    SupabaseAuthorizationError,
    SupabaseError,
    SupabaseStorageError,
    map_storage_error,
    map_auth_error,
    SupabaseTimeoutError,
)
from functools import wraps, lru_cache
from concurrent.futures import ThreadPoolExecutor
from tenacity import retry, stop_after_attempt, wait_exponential
from supabase.lib.client_options import ClientOptions
from gotrue.errors import AuthApiError
from gotrue import AsyncMemoryStorage, SyncMemoryStorage, AsyncGoTrueClient
from dataclasses import dataclass
from typing import List, Dict, Any
from dotenv import load_dotenv


def make_sync(async_func):
    """Decorator to convert async methods to sync methods."""

    @wraps(async_func)
    def sync_wrapper(*args, **kwargs):
        try:
            loop = asyncio.get_event_loop()
        except RuntimeError:
            # If no event loop exists, create a new one
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)

        if loop.is_running():
            # If we're in a running event loop, use a thread
            with ThreadPoolExecutor(max_workers=1) as executor:
                future = executor.submit(
                    lambda: asyncio.run(async_func(*args, **kwargs))
                )
                return future.result()
        else:
            # If no loop is running, we can just run it directly
            return loop.run_until_complete(async_func(*args, **kwargs))

    return sync_wrapper


def log_basic():
    """Basic logging decorator that logs method entry and exit."""

    def decorator(func):
        @wraps(func)
        async def wrapper(*args, **kwargs):
            logger = Logger(func.__module__)
            logger.debug(f"Entering {func.__name__}")
            try:
                result = await func(*args, **kwargs)
                logger.debug(f"Exiting {func.__name__}")
                return result
            except Exception as e:
                logger.error(f"Error in {func.__name__}: {str(e)}")
                raise

        return wrapper

    return decorator


class SupabaseService:
    """Service class for interacting with Supabase.

    Provides methods for database operations, authentication, storage,
    and realtime subscriptions.

    Attributes:
        url (str): Supabase project URL
        api_key (str): Supabase API key
        logger: Logger instance for this service
    """

    DEFAULT_TIMEOUT = 30  # seconds
    MAX_RETRIES = 3
    CHUNK_SIZE = 1000  # for bulk operations
    STORAGE_UPLOAD_LIMIT = 50 * 1024 * 1024  # 50MB
    ALLOWED_OPERATORS: List[FilterOperator] = [
        "eq",  # equals
        "neq",  # not equals
        "gt",  # greater than
        "gte",  # greater than or equal
        "lt",  # less than
        "lte",  # less than or equal
        "like",  # LIKE operator
        "ilike",  # case insensitive LIKE
        "is",  # IS operator (for null)
        "in",  # IN operator
        "contains",  # contains for arrays/json
        "contained_by",  # contained by for arrays/json
        "text_search",  # full text search
    ]

    MAX_BATCH_SIZE = 1000
    TIMEOUT_SECONDS = 30
    RETRY_ATTEMPTS = 3

    def __init__(self, url: str, api_key: str):
        if not url or not api_key:
            raise SupabaseError("URL and API key are required")
        self.url = url
        self.api_key = api_key
        self._logger = Logger(self.__class__.__name__)
        self._init_client()
        self._constraint_cache = {}
        self._cache_timeout = timedelta(minutes=5)  # Cache for 5 minutes

    @log_method()
    def _init_client(self) -> None:
        """Initialize the Supabase async client."""
        try:
            options = ClientOptions(
                schema="public",
                headers={"x-my-custom-header": "my-app-name"},
                persist_session=True,
                auto_refresh_token=True,
                postgrest_client_timeout=self.DEFAULT_TIMEOUT,
            )

            # Create the client
            client = AsyncClient(self.url, self.api_key, options=options)

            if not client:
                raise SupabaseConnectionError("Failed to create AsyncClient")

            # Initialize storage for auth
            storage = AsyncMemoryStorage()

            # Create and set auth client with storage
            auth_client = AsyncGoTrueClient(
                url=f"{self.url}/auth/v1",
                headers={"apikey": self.api_key},
                storage=storage,
            )
            client.auth = auth_client

            self._supabase = client

            # Add detailed debugging
            self._logger.debug(f"""
            Client initialization details:
            - Client exists: {bool(self._supabase)}
            - Auth exists: {bool(self._supabase.auth)}
            - Auth type: {type(self._supabase.auth)}
            - Auth storage exists: {bool(self._supabase.auth._storage)}
            - URL valid: {bool(self.url)}
            - API key valid: {bool(self.api_key)}
            """)

        except Exception as e:
            self._logger.error(f"Failed to initialize Supabase client: {str(e)}")
            raise SupabaseConnectionError(
                "Failed to initialize client", original_error=e
            )

    @property
    def supabase(self) -> AsyncClient:
        """Get the Supabase client instance.

        Returns:
            AsyncClient: The initialized Supabase client

        Raises:
            SupabaseConnectionError: If client is not properly initialized
        """
        if not hasattr(self, "_supabase") or not isinstance(
            self._supabase, AsyncClient
        ):
            self._logger.error("Supabase client not properly initialized")
            raise SupabaseConnectionError("Supabase client not properly initialized")
        return self._supabase

    @property
    def logger(self) -> Logger:
        """Get the logger instance for this service.

        Returns:
            Logger: The logger instance used by this service
        """
        return self._logger

    @log_method()
    async def select_from_table(
        self,
        table_name: str,
        fields: Union[Literal["*"], List[str]],
        where_filters: Optional[
            List[Tuple[str, Literal["eq", "neq", "gt", "lt", ...], Any]]
        ] = None,
        limit: Optional[int] = None,
        offset: Optional[int] = None,
        order_by: Optional[Dict[ColumnName, Literal["asc", "desc"]]] = None,
        validate_constraints: bool = False,
    ) -> List[Dict[str, Any]]:
        """Select records from a table with proper error handling.

        Args:
            table_name: Name of the table to query
            fields: List of fields to select or "*" for all fields
            where_filters: Optional list of filters to apply
            limit: Optional limit on number of records
            offset: Optional offset for pagination
            order_by: Optional ordering configuration
            validate_constraints: Whether to validate against table constraints (default False)

        Returns:
            List[Dict[str, Any]]: Selected records or None if no results

        Raises:
            SupabaseQueryError: If the select operation fails or validation fails
        """

        async def _select_operation():
            try:
                self._validate_table_name(table_name)

                # Validate field constraints if enabled
                if validate_constraints and fields != "*":
                    self._logger.debug(
                        f"Validating field constraints for table {table_name}"
                    )
                    # Create a dummy record with the requested fields for validation
                    dummy_record = {field: None for field in fields}
                    cache_key = self._get_cache_key(table_name, dummy_record)
                    cached_result = self._get_cached_validation(cache_key)

                    if cached_result is None:
                        await self.validate_select_against_constraints(
                            table_name, dummy_record
                        )
                        self._set_cached_validation(cache_key)

                query = self.supabase.table(table_name)
                fields_str = (
                    fields
                    if isinstance(fields, str)
                    else ",".join(cast(List[str], fields))
                )
                query = query.select(fields_str)

                if where_filters:
                    # Validate where_filters fields if constraint validation is enabled
                    if validate_constraints:
                        filter_fields = {filter[0]: None for filter in where_filters}
                        cache_key = self._get_cache_key(table_name, filter_fields)
                        cached_result = self._get_cached_validation(cache_key)

                        if cached_result is None:
                            await self.validate_select_against_constraints(
                                table_name, filter_fields
                            )
                            self._set_cached_validation(cache_key)

                    # Serialize datetime objects in filters
                    serialized_filters = [
                        (
                            column,
                            operator,
                            self._serialize_data({"value": value})["value"],
                        )
                        for column, operator, value in where_filters
                    ]

                    for column, operator, value in serialized_filters:
                        query = self._apply_filter(query, column, operator, value)

                if limit is not None:
                    if not isinstance(limit, int) or limit < 0:
                        raise SupabaseQueryError("Invalid limit value")
                    query = query.limit(limit)

                if offset is not None:
                    if not isinstance(offset, int) or offset < 0:
                        raise SupabaseQueryError("Invalid offset value")
                    query = query.offset(offset)

                if order_by:
                    # Validate order_by fields if constraint validation is enabled
                    if validate_constraints:
                        order_fields = {field: None for field in order_by.keys()}
                        cache_key = self._get_cache_key(table_name, order_fields)
                        cached_result = self._get_cached_validation(cache_key)

                        if cached_result is None:
                            await self.validate_select_against_constraints(
                                table_name, order_fields
                            )
                            self._set_cached_validation(cache_key)

                    for column, direction in order_by.items():
                        query = query.order(f"{column}.{direction}")

                response = await query.execute()

                if validate_constraints:
                    self._logger.debug(
                        f"Select passed constraint validation for table {table_name}"
                    )

                return response.data if response.data else None

            except Exception as e:
                error_msg = f"Select operation failed: {str(e)}"
                if validate_constraints:
                    error_msg = f"Select validation/operation failed: {str(e)}"
                raise SupabaseQueryError(error_msg, original_error=e)

        return await self._execute_supabase_operation("select", _select_operation)

    async def select_from_table_new(
        self,
        table_name: TableName,
        fields: Union[Literal["*"], List[str]],  # Simplified from ColumnName
        where_filters: Optional[List[Tuple[str, FilterOperator, Any]]] = None,
    ) -> List[Dict[str, Any]]:  # More accurate return type
        """Select records from a table with proper error handling.

        Args:
            table_name: Name of the table to select from
            fields: List of column names or "*" for all columns
            where_filters: Optional list of filter conditions in format (column, operator, value)

        Returns:
            List of records matching the query criteria

        Raises:
            SupabaseError: If query fails
            SupabaseAuthorizationError: If permission denied
            SupabaseTimeoutError: If query times out
        """
        try:
            # Build base query
            query = self.client.table(table_name).select(fields)

            # Add any filter conditions
            if where_filters:
                for column, operator, value in where_filters:
                    query = query.filter(column, operator, value)

            # Execute query
            response = await query.execute()

            return response.data if response else []

        except Exception as e:
            # Map errors to custom exceptions
            if isinstance(e, AuthApiError):
                raise map_auth_error(e)
            elif "timeout" in str(e).lower():
                raise SupabaseTimeoutError(str(e))
            else:
                raise SupabaseError(f"Error selecting from {table_name}: {str(e)}")

    async def insert_into_table_new(
        self,
        table_name: TableName,
        insert_fields: Dict[str, Any],  # Simplified from FieldValue
        upsert: bool = False,
    ) -> InsertResult:
        """Insert records with proper error handling."""
        try:
            # Build query
            query = self.client.table(table_name)

            # Execute insert with upsert flag
            if upsert:
                response = await query.upsert(insert_fields).execute()
            else:
                response = await query.insert(insert_fields).execute()

            # Extract data from response
            data = response.data if response else []
            count = len(data)

            return InsertResult(count=count, data=data)

        except Exception as e:
            # Map errors to custom exceptions
            if isinstance(e, AuthApiError):
                raise map_auth_error(e)
            elif "timeout" in str(e).lower():
                raise SupabaseTimeoutError(str(e))
            else:
                raise SupabaseError(f"Error inserting into {table_name}: {str(e)}")

    @log_method()
    async def insert_into_table(
        self,
        table_name: TableName,
        insert_fields: Union[
            Dict[ColumnName, FieldValue], List[Dict[ColumnName, FieldValue]]
        ],
        upsert: bool = False,
        returning: ReturnType = "representation",
        ignore_duplicates: bool = False,
        validate_constraints: bool = False,
    ) -> InsertResult:
        """Insert records with proper error handling."""

        async def _insert_operation():
            try:
                self._validate_table_name(table_name)

                # Convert single record to list for consistent handling
                records_to_insert = (
                    [insert_fields]
                    if isinstance(insert_fields, dict)
                    else insert_fields
                )

                # Validate constraints if enabled
                if validate_constraints:
                    self._logger.debug(f"Validating constraints for table {table_name}")

                    # Validate insert fields
                    for record in records_to_insert:
                        cache_key = self._get_cache_key(table_name, record)
                        cached_result = self._get_cached_validation(cache_key)

                        if cached_result is None:
                            await self.validate_update_against_constraints(
                                table_name, record
                            )
                            self._set_cached_validation(cache_key)

                    # If upsert is True, validate the id field exists
                    if upsert and not ignore_duplicates:
                        id_fields = {"id": None}
                        cache_key = self._get_cache_key(table_name, id_fields)
                        cached_result = self._get_cached_validation(cache_key)

                        if cached_result is None:
                            await self.validate_select_against_constraints(
                                table_name, id_fields
                            )
                            self._set_cached_validation(cache_key)

                # Validate returning parameter
                if returning not in ["minimal", "representation"]:
                    raise SupabaseQueryError(f"Invalid returning value: {returning}")

                # Serialize datetime objects to ISO format
                serialized_fields = self._serialize_data(records_to_insert)

                self._validate_batch_size(serialized_fields)
                if not serialized_fields:
                    raise SupabaseQueryError("Empty insert batch")
                if not all(isinstance(record, dict) for record in serialized_fields):
                    raise SupabaseQueryError("Invalid record format in batch")

                query = self.supabase.table(table_name)

                if upsert:
                    query = query.upsert(
                        serialized_fields,
                        on_conflict=None if ignore_duplicates else "id",
                        returning=returning,
                    )
                else:
                    query = query.insert(serialized_fields, returning=returning)

                response = await query.execute()

                records = (
                    response.data[0]
                    if isinstance(insert_fields, dict)
                    else response.data
                )

                if validate_constraints:
                    self._logger.debug(
                        f"Insert passed constraint validation for table {table_name}"
                    )

                return InsertResult(
                    count=len(response.data),
                    records=records if isinstance(records, list) else [records],
                )

            except Exception as e:
                error_msg = f"Insert operation failed: {str(e)}"
                if validate_constraints:
                    error_msg = f"Insert validation/operation failed: {str(e)}"
                raise SupabaseQueryError(error_msg, original_error=e)

        return await self._execute_supabase_operation("insert", _insert_operation)

    def _get_cache_key(self, table_name: str, update_fields: Dict[str, Any]) -> str:
        """Generate a cache key from table name and update fields."""
        # Sort update_fields to ensure consistent cache keys
        sorted_fields = json.dumps(update_fields, sort_keys=True)
        key = f"{table_name}:{sorted_fields}"
        return hashlib.md5(key.encode()).hexdigest()

    def _get_cached_validation(self, cache_key: str) -> Optional[bool]:
        """Get validation result from cache if not expired."""
        if cache_key in self._constraint_cache:
            timestamp, result = self._constraint_cache[cache_key]
            if datetime.now() - timestamp < self._cache_timeout:
                self._logger.debug(
                    f"Using cached validation result for key {cache_key}"
                )
                return result
            else:
                # Remove expired cache entry
                del self._constraint_cache[cache_key]
        return None

    def _set_cached_validation(self, cache_key: str) -> None:
        """Cache successful validation result."""
        self._constraint_cache[cache_key] = (datetime.now(), True)

    def clear_validation_cache(self, table_name: Optional[str] = None) -> None:
        """Clear validation cache for a specific table or all tables."""
        if table_name:
            # Clear only entries for specific table
            keys_to_remove = [
                k
                for k in self._constraint_cache.keys()
                if k.startswith(f"{table_name}:")
            ]
            for k in keys_to_remove:
                del self._constraint_cache[k]
        else:
            self._constraint_cache.clear()
        self._logger.debug(
            f"Cleared validation cache for {'all tables' if table_name is None else table_name}"
        )

    @log_method()
    async def validate_update_against_constraints(
        self, table_name: str, update_fields: Dict[str, Any]
    ) -> None:
        """Validate update fields against table constraints with caching."""
        cache_key = self._get_cache_key(table_name, update_fields)

        # Check cache first
        cached_result = self._get_cached_validation(cache_key)
        if cached_result is not None:
            return

        try:
            constraints = await self.get_table_constraints(table_name)

            # Check NOT NULL constraints
            for column in constraints["not_null"]:
                if column in update_fields and update_fields[column] is None:
                    raise SupabaseQueryError(f"Column '{column}' cannot be NULL")
                if column == "priority" and column not in update_fields:
                    raise SupabaseQueryError(
                        f"Column '{column}' is required for updates"
                    )

            # Check CHECK constraints
            if constraints["check"]:
                for check in constraints["check"]:
                    column = check["column"]
                    if column in update_fields:
                        constraint_def = check["constraint"]
                        value = update_fields[column]

                        if "ANY" in constraint_def or "IN" in constraint_def:
                            allowed_values = re.findall(r"'([^']*)'", constraint_def)
                            if str(value) not in allowed_values:
                                raise SupabaseQueryError(
                                    f"Value '{value}' for column '{column}' violates check constraint. "
                                    f"Allowed values are: {allowed_values}"
                                )

            # Cache successful validation
            self._set_cached_validation(cache_key)
            self._logger.debug(
                f"Update fields validation passed for table {table_name}"
            )

        except Exception as e:
            if isinstance(e, SupabaseQueryError):
                raise
            raise SupabaseQueryError(f"Validation failed: {str(e)}")

    @log_method()
    async def update_table(
        self,
        table_name: TableName,
        update_fields: Dict[ColumnName, FieldValue],
        where_filters: List[WhereFilter],
        validate_constraints: bool = False,  # Default to False for production
    ) -> Optional[ResponseRecord]:
        """Update records in a Supabase table with dynamic filtering.

        Args:
            table_name: Name of the table to update
            update_fields: Dictionary of fields to update
            where_filters: List of filters to apply
            validate_constraints: Whether to validate against table constraints (default False)

        Returns:
            Optional[ResponseRecord]: Updated record if successful

        Raises:
            SupabaseQueryError: If update fails or validation fails
        """

        async def _update_operation():
            try:
                self._validate_table_name(table_name)

                # Validate constraints if enabled
                if validate_constraints:
                    self._logger.debug(f"Validating constraints for table {table_name}")
                    await self.validate_update_against_constraints(
                        table_name, update_fields
                    )

                # Serialize datetime objects to ISO format
                serialized_fields = self._serialize_data(update_fields)

                if not isinstance(serialized_fields, dict) or not serialized_fields:
                    raise SupabaseQueryError("Invalid or empty update fields")

                query = self.supabase.table(table_name).update(serialized_fields)

                # Apply filters
                for column, operator, value in where_filters:
                    query = self._apply_filter(query, column, operator, value)

                response = await query.execute()
                result = response.data[0] if response.data else None

                if validate_constraints:
                    self._logger.debug(
                        f"Update passed constraint validation for table {table_name}"
                    )

                return result

            except Exception as e:
                error_msg = f"Update operation failed: {str(e)}"
                if validate_constraints:
                    error_msg = f"Update validation/operation failed: {str(e)}"
                raise SupabaseQueryError(error_msg, original_error=e)

        return await self._execute_supabase_operation("update", _update_operation)

    @log_method()
    async def delete_from_table(
        self,
        table_name: TableName,
        where_filters: List[WhereFilter],
        returning: ReturnType = "representation",
    ) -> Tuple[bool, int]:
        """Delete records from a table with proper error handling and validation.

        Args:
            table_name (TableName): Name of the table to delete from.
            where_filters (List[WhereFilter]): List of tuples containing (column, operator, value) for filters.
                Example: [
                    ("id", "eq", 123),
                    ("name", "like", "%test%"),
                    ("email", "ilike", "%@example.com")
                ]
            returning (ReturnType, optional): Format of returned data.
                Defaults to "representation". Options are "minimal" or "representation".

        Returns:
            Tuple[bool, int]: Tuple containing (success, total number of records deleted)

        Raises:
            SupabaseQueryError: If the delete operation fails or if invalid operators are provided
            ValueError: If table_name is empty or where_filters is empty
        """
        try:
            total_deleted = 0
            allowed_operators = {"eq", "like", "ilike"}

            self._validate_table_name(table_name)

            if not where_filters:
                raise SupabaseQueryError(
                    "Where filters are required for delete operations",
                    details="Delete operations require explicit filters for safety",
                )

            # Process each filter with its own delete operation
            for column, operator, value in where_filters:
                if operator not in allowed_operators:
                    error_msg = f"Invalid delete operator: '{operator}'"
                    details = f"Only operators {allowed_operators} are supported for delete operations, but got '{operator}'"
                    self._logger.error(f"{error_msg} - {details}")
                    raise SupabaseQueryError(error_msg, details=details)

                # Submit a single delete operation for this filter
                query = self.supabase.table(table_name).delete(returning=returning)

                # Apply the appropriate filter based on operator
                if operator == "eq":
                    query = query.eq(column, value)
                elif operator == "like":
                    query = query.like(column, value)
                elif operator == "ilike":
                    query = query.ilike(column, value)

                response = await query.execute()
                deleted_count = len(response.data) if response.data else 0
                total_deleted += deleted_count

                self._logger.debug(
                    f"Deleted {deleted_count} records with filter: {column} {operator} {value}"
                )

            return True, total_deleted

        except SupabaseQueryError:
            # Re-raise SupabaseQueryError without wrapping it
            raise
        except Exception as e:
            error_msg = f"Failed to delete from {table_name}"
            self._logger.error(f"{error_msg}: {str(e)}")
            raise SupabaseQueryError(error_msg, original_error=e)

    @log_method()
    async def login(self, email: str, password: str) -> bool:
        """Login with email and password."""
        try:
            if not email or not password:
                raise SupabaseAuthenticationError("Email and password are required")

            response = await self.supabase.auth.sign_in_with_password(
                {"email": email, "password": password}
            )

            if not response.user:
                raise SupabaseAuthenticationError("Login failed - no user returned")

            return True

        except AuthApiError as e:
            raise map_auth_error(e)
        except Exception as e:
            raise SupabaseAuthenticationError("Login failed", original_error=e)

    @log_method()
    async def logout(self) -> bool:
        """Logout the current user."""
        try:
            await self.supabase.auth.sign_out()
            return True

        except AuthApiError as e:
            raise map_auth_error(e)
        except Exception as e:
            raise SupabaseAuthenticationError("Logout failed", original_error=e)

    @log_method()
    async def refresh_session(self) -> bool:
        """Refresh the current session."""
        try:
            response = await self.supabase.auth.refresh_session()
            if not response.session:
                raise SupabaseSessionError(
                    "Session refresh failed - no session returned"
                )
            return True

        except AuthApiError as e:
            raise map_auth_error(e)
        except Exception as e:
            raise SupabaseTokenRefreshError(
                "Failed to refresh session", original_error=e
            )

    @log_method()
    async def get_user(self):
        """Get the current user."""
        try:
            response = await self.supabase.auth.get_user()
            if not response.user:
                raise SupabaseSessionMissingError("No active session found")
            return response.user

        except AuthApiError as e:
            raise map_auth_error(e)
        except Exception as e:
            raise SupabaseAuthenticationError("Failed to get user", original_error=e)

    @log_method()
    async def signup(self, email: str, password: str) -> bool:
        """Sign up a new user."""
        try:
            if not email or not password:
                raise SupabaseAuthenticationError("Email and password are required")

            response = await self.supabase.auth.sign_up(
                {"email": email, "password": password}
            )

            if not response.user:
                raise SupabaseAuthenticationError("Signup failed - no user created")

            return True

        except AuthApiError as e:
            raise map_auth_error(e)
        except Exception as e:
            raise SupabaseAuthenticationError("Signup failed", original_error=e)

    @log_method()
    def _serialize_data(
        self, data: Union[Dict[str, Any], List[Dict[str, Any]]]
    ) -> Union[Dict[str, Any], List[Dict[str, Any]]]:
        """Serialize data for Supabase by converting Python types to JSON-compatible types."""

        def _serialize_value(value: Any) -> Any:
            if isinstance(value, datetime):
                return value.isoformat()
            if isinstance(value, (list, tuple)):
                return [_serialize_value(v) for v in value]
            if isinstance(value, dict):
                return {k: _serialize_value(v) for k, v in value.items()}
            return value

        if isinstance(data, list):
            return [
                _serialize_value(item) if isinstance(item, dict) else item
                for item in data
            ]
        return _serialize_value(data)

    @log_method()
    async def verify_email(self, token: str, email: str) -> bool:
        """Verify email with token."""
        try:
            await self.supabase.auth.verify_otp(
                {"email": email, "token": token, "type": "email"}
            )
            return True

        except AuthApiError as e:
            raise map_auth_error(e)
        except Exception as e:
            raise SupabaseEmailVerificationError(
                "Email verification failed", original_error=e
            )

    @log_method()
    async def set_current_domain(self, domain_id: Optional[str]) -> None:
        """Set the current domain for subsequent Supabase operations.

        Args:
            domain_id: ID of the domain to set as current, or None to clear

        Raises:
            Exception: If the server returns an invalid response
        """
        try:
            response = await self.supabase.rpc(
                "set_current_domain", {"domain_id": domain_id}
            ).execute()

            if not hasattr(response, "data"):
                raise Exception("Invalid response from server")
        except Exception as e:
            raise SupabaseAuthorizationError(
                "Failed to set current domain", original_error=e
            )

    # Storage Methods
    @log_method()
    async def upload_file(
        self, bucket: str, file_path: str, file_data: bytes, content_type: str = None
    ) -> str:
        """Upload a file to Supabase Storage.

        Args:
            bucket: Storage bucket name
            file_path: Path where file will be stored
            file_data: Binary file data
            content_type: MIME type of the file

        Returns:
            str: Public URL of the uploaded file

        Raises:
            ValueError: If invalid parameters are provided
            SupabaseStorageAuthError: If storage authentication fails
            SupabaseStoragePermissionError: If insufficient permissions
            SupabaseStorageQuotaError: If storage quota is exceeded
            SupabaseStorageValidationError: If file validation fails
            SupabaseStorageError: For other storage-related errors
        """
        if not bucket or not isinstance(bucket, str):
            raise ValueError("Bucket must be a non-empty string")
        if not file_data:
            raise ValueError("File data cannot be empty")
        if not file_path or not isinstance(file_path, str):
            raise ValueError("File path must be a non-empty string")

        try:
            response = await self.supabase.storage.from_(bucket).upload(
                file_path,
                file_data,
                {"content-type": content_type} if content_type else None,
            )
            if not response or "Key" not in response:
                raise SupabaseStorageError("Invalid response from storage upload")
            return response["Key"]
        except StorageApiError as e:
            raise map_storage_error(e)
        except Exception as e:
            raise SupabaseStorageError("Failed to upload file", original_error=e)

    @log_method()
    async def download_file(self, bucket: str, file_path: str) -> bytes:
        """Download a file from Supabase Storage.

        Args:
            bucket: Storage bucket name
            file_path: Path to the file

        Returns:
            bytes: File data

        Raises:
            ValueError: If invalid parameters are provided
            SupabaseStorageAuthError: If storage authentication fails
            SupabaseStoragePermissionError: If insufficient permissions
            SupabaseStorageNotFoundError: If file not found
            SupabaseStorageError: For other storage-related errors
        """
        if not bucket or not isinstance(bucket, str):
            raise ValueError("Bucket must be a non-empty string")
        if not file_path or not isinstance(file_path, str):
            raise ValueError("File path must be a non-empty string")

        try:
            response = await self.supabase.storage.from_(bucket).download(file_path)
            if not response:
                raise SupabaseStorageError("No data received from storage download")
            return response
        except StorageApiError as e:
            raise map_storage_error(e)
        except Exception as e:
            raise SupabaseStorageError("Failed to download file", original_error=e)

    @log_method()
    async def delete_file(self, bucket: str, file_paths: list[str]) -> bool:
        """Delete files from Supabase Storage.

        Args:
            bucket: Storage bucket name
            file_paths: List of file paths to delete

        Returns:
            bool: True if deletion was successful

        Raises:
            ValueError: If invalid parameters are provided
            SupabaseStorageAuthError: If storage authentication fails
            SupabaseStoragePermissionError: If insufficient permissions
            SupabaseStorageNotFoundError: If any file not found
            SupabaseStorageError: For other storage-related errors
        """
        if not bucket or not isinstance(bucket, str):
            raise ValueError("Bucket must be a non-empty string")
        if not file_paths or not isinstance(file_paths, list):
            raise ValueError("File paths must be a non-empty list")
        if not all(isinstance(path, str) for path in file_paths):
            raise ValueError("All file paths must be strings")

        try:
            await self.supabase.storage.from_(bucket).remove(file_paths)
            return True
        except StorageApiError as e:
            raise map_storage_error(e)
        except Exception as e:
            raise SupabaseStorageError("Failed to delete files", original_error=e)

    @log_method()
    async def list_files(self, bucket: str, path: str = "") -> list[dict]:
        """List files in a storage bucket.

        Args:
            bucket: Storage bucket name
            path: Optional path prefix to filter by

        Returns:
            list[dict]: List of file metadata

        Raises:
            ValueError: If invalid parameters are provided
            SupabaseStorageAuthError: If storage authentication fails
            SupabaseStoragePermissionError: If insufficient permissions
            SupabaseStorageNotFoundError: If bucket not found
            SupabaseStorageError: For other storage-related errors
        """
        if not bucket or not isinstance(bucket, str):
            raise ValueError("Bucket must be a non-empty string")
        if not isinstance(path, str):
            raise ValueError("Path must be a string")

        try:
            response = await self.supabase.storage.from_(bucket).list(path)
            if response is None:
                return []
            return response
        except StorageApiError as e:
            raise map_storage_error(e)
        except Exception as e:
            raise SupabaseStorageError("Failed to list files", original_error=e)

    # Enhanced Authentication Methods
    @log_method()
    async def login_with_provider(
        self, provider: str, redirect_url: str = None
    ) -> Dict[str, Any]:
        """Login with OAuth provider (Google, GitHub, etc.).

        Args:
            provider: OAuth provider name
            redirect_url: URL to redirect after authentication

        Returns:
            dict: Provider session information
        """
        try:
            response = await self.supabase.auth.sign_in_with_oauth(
                {
                    "provider": provider,
                    "options": {"redirect_to": redirect_url} if redirect_url else None,
                }
            )
            return response
        except Exception as e:
            raise SupabaseAuthenticationError(
                f"Failed to login with {provider}", original_error=e
            )

    @log_method()
    async def update_user(self, user_data: dict) -> Any:
        """Update user data."""
        try:
            response = await self.supabase.auth.update_user(user_data)
            if not response.user:
                raise SupabaseAuthenticationError(
                    "User update failed - no user returned"
                )
            return response.user

        except AuthApiError as e:
            raise map_auth_error(e)
        except Exception as e:
            raise SupabaseAuthenticationError("Failed to update user", original_error=e)

    # Role-Based Access Control Methods
    @log_method()
    async def get_user_roles(
        self, user_id: Optional[str] = None
    ) -> List[Dict[str, Any]]:
        """
        Returns user roles with additional metadata
        Example return: [{"role": "admin", "assigned_at": "2024-01-01"}]
        """
        try:
            response = await self.supabase.rpc(
                "get_user_roles", {"p_user_id": user_id}
            ).execute()
            return response.data
        except Exception as e:
            raise SupabaseAuthorizationError(
                "Failed to get user roles", original_error=e
            )

    @log_method()
    async def check_permission(self, permission: str) -> bool:
        """Check if current user has specific permission.

        Args:
            permission: Permission to check

        Returns:
            bool: True if user has permission
        """
        try:
            response = await self.supabase.rpc(
                "check_permission", {"p_permission": permission}
            ).execute()
            return response.data
        except Exception as e:
            raise SupabaseAuthorizationError(
                "Failed to check permission", original_error=e
            )

    # Realtime Subscription Methods
    @log_method()
    async def subscribe_to_table(
        self,
        table_name: str,
        callback: Callable[[Dict[str, Any]], None],
        event: str = "*",
        filter_str: Optional[str] = None,
    ) -> Any:
        """Subscribe to real-time changes on a table.

        Args:
            table_name: Name of table to subscribe to
            callback: Function to call when changes occur
            event: Event type to listen for ("INSERT", "UPDATE", "DELETE", or "*")
            filter_str: Optional filter string
        """
        try:
            channel = self.supabase.channel("db-changes")
            channel.on(
                "postgres_changes",
                event=event,
                schema="public",
                table=table_name,
                filter=filter_str,
                callback=callback,
            )
            await channel.subscribe()
            return channel
        except Exception as e:
            raise SupabaseError("Failed to create subscription", original_error=e)

    # Storage Bucket Management Methods
    @log_method()
    async def create_bucket(self, bucket_name: str, is_public: bool = False) -> dict:
        """Create a new storage bucket.

        Args:
            bucket_name: Name of the bucket to create
            is_public: Whether the bucket should be public

        Returns:
            dict: Created bucket information

        Raises:
            ValueError: If invalid parameters are provided
            SupabaseStorageAuthError: If storage authentication fails
            SupabaseStoragePermissionError: If insufficient permissions
            SupabaseStorageValidationError: If bucket name is invalid
            SupabaseStorageError: For other storage-related errors
        """
        if not bucket_name or not isinstance(bucket_name, str):
            raise ValueError("Bucket name must be a non-empty string")
        if not isinstance(is_public, bool):
            raise ValueError("is_public must be a boolean")

        try:
            response = await self.supabase.storage.create_bucket(
                bucket_name, {"public": is_public}
            )
            if not response:
                raise SupabaseStorageError("Invalid response from bucket creation")
            return response
        except StorageApiError as e:
            raise map_storage_error(e)
        except Exception as e:
            raise SupabaseStorageError("Failed to create bucket", original_error=e)

    @log_method()
    async def get_bucket(self, bucket_name: str) -> dict:
        """Get bucket information.

        Args:
            bucket_name: Name of the bucket

        Returns:
            dict: Bucket information
        """
        try:
            return await self.supabase.storage.get_bucket(bucket_name)
        except Exception as e:
            raise SupabaseError("Failed to get bucket", original_error=e)

    @log_method()
    async def list_buckets(self) -> list[dict]:
        """List all storage buckets.

        Returns:
            list[dict]: List of bucket information
        """
        try:
            return await self.supabase.storage.list_buckets()
        except Exception as e:
            raise SupabaseError("Failed to list buckets", original_error=e)

    @log_method()
    async def delete_bucket(self, bucket_name: str) -> bool:
        """Delete a storage bucket.

        Args:
            bucket_name: Name of the bucket to delete

        Returns:
            bool: True if deletion was successful

        Raises:
            ValueError: If invalid parameters are provided
            SupabaseStorageAuthError: If storage authentication fails
            SupabaseStoragePermissionError: If insufficient permissions
            SupabaseStorageNotFoundError: If bucket not found
            SupabaseStorageError: For other storage-related errors
        """
        if not bucket_name or not isinstance(bucket_name, str):
            raise ValueError("Bucket name must be a non-empty string")

        try:
            await self.supabase.storage.delete_bucket(bucket_name)
            return True
        except StorageApiError as e:
            raise map_storage_error(e)
        except Exception as e:
            raise SupabaseStorageError("Failed to delete bucket", original_error=e)

    @log_method()
    async def empty_bucket(self, bucket_name: str) -> bool:
        """Empty a storage bucket.

        Args:
            bucket_name: Name of the bucket to empty

        Returns:
            bool: True if operation was successful

        Raises:
            ValueError: If invalid parameters are provided
            SupabaseStorageAuthError: If storage authentication fails
            SupabaseStoragePermissionError: If insufficient permissions
            SupabaseStorageNotFoundError: If bucket not found
            SupabaseStorageError: For other storage-related errors
        """
        if not bucket_name or not isinstance(bucket_name, str):
            raise ValueError("Bucket name must be a non-empty string")

        try:
            await self.supabase.storage.empty_bucket(bucket_name)
            return True
        except StorageApiError as e:
            raise map_storage_error(e)
        except Exception as e:
            raise SupabaseStorageError("Failed to empty bucket", original_error=e)

    # RPC Methods
    @log_method()
    async def rpc(self, function_name: str, params: dict = None) -> Any:
        """Call a Postgres function via RPC.

        Args:
            function_name: Name of the function to call
            params: Optional parameters for the function

        Returns:
            Any: Function result
        """
        try:
            response = await self.supabase.rpc(function_name, params or {}).execute()
            return response.data
        except Exception as e:
            raise SupabaseError(f"RPC call to {function_name} failed", original_error=e)

    # Add sync versions for new methods

    # Enhanced Authentication Methods
    @log_method()
    async def update_password(self, new_password: str) -> bool:
        """Update password for the currently logged-in user.

        Args:
            new_password: The new password to set

        Returns:
            bool: True if password was updated successfully
        """
        try:
            await self.supabase.auth.update_user({"password": new_password})
            return True
        except Exception as e:
            raise SupabaseAuthenticationError(
                "Failed to update password", original_error=e
            )

    @log_method()
    async def verify_otp(self, email: str, token: str) -> bool:
        """Verify one-time password token.

        Args:
            email: User's email address
            token: OTP token to verify

        Returns:
            bool: True if verification successful
        """
        try:
            await self.supabase.auth.verify_otp(
                {"email": email, "token": token, "type": "email"}
            )
            return True
        except Exception as e:
            raise SupabaseAuthenticationError("Failed to verify OTP", original_error=e)

    @log_method()
    async def set_session(self, access_token: str, refresh_token: str) -> bool:
        """Manually set the session tokens.

        Args:
            access_token: JWT access token
            refresh_token: Refresh token

        Returns:
            bool: True if session was set successfully
        """
        try:
            await self.supabase.auth.set_session(access_token, refresh_token)
            return True
        except Exception as e:
            raise SupabaseAuthenticationError("Failed to set session", original_error=e)

    # Advanced Query Methods
    @log_method()
    async def select_with_join(
        self,
        table_name: str,
        foreign_table: str,
        fields: list[str],
        join_column: str,
        foreign_key: str,
        where_filters: list = None,
    ) -> list:
        """Select data with a JOIN operation.

        Args:
            table_name: Primary table name
            foreign_table: Table to join with
            fields: List of fields to select (format: ["table1.field1", "table2.field2"])
            join_column: Column from primary table for joining
            foreign_key: Column from foreign table for joining
            where_filters: Optional filters in format [(column, operator, value)]

        Returns:
            list: Query results with joined data

        Raises:
            SupabaseQueryError: If the join operation fails
            ValueError: If invalid join parameters are provided
        """
        try:
            query = (
                self.supabase.from_(table_name)
                .select(",".join(fields))
                .join(foreign_table, f"{join_column}=eq.{foreign_key}")
            )

            if where_filters:
                for filter in where_filters:
                    column, operator, value = filter
                    query = self._apply_filter(query, column, operator, value)

            response = await query.execute()
            return response.data
        except Exception as e:
            raise SupabaseQueryError("Failed to execute join query", original_error=e)

    @retry(
        stop=stop_after_attempt(3), wait=wait_exponential(multiplier=1, min=4, max=10)
    )
    @log_method()
    async def cleanup(self):
        """Cleanup resources when service is no longer needed."""
        try:
            await self.supabase.auth.sign_out()
            # Add any other cleanup needed
        except Exception as e:
            self._logger.error("Error during cleanup", error=e)

    async def __aenter__(self):
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        await self.cleanup()

    def _is_token_expiring_soon(self, token: str, threshold_minutes: int = 5) -> bool:
        # Add JWT expiration checking logic
        pass

    async def _ensure_connected(self):
        """Ensure connection is available before operations."""
        if not await self.check_connection():
            await self._init_client()  # Reinitialize if needed

    async def create_search_index(self, table_name: str, column_name: str) -> bool:
        """
        Create a GIN index for full-text search on a column.

        Args:
            table_name: Name of the table
            column_name: Name of the column to index

        Returns:
            bool: True if index was created successfully
        """
        try:
            # Create a generated column for text search
            await self.supabase.rpc(
                "execute_sql",
                {
                    "query": f"""
                ALTER TABLE {table_name} 
                ADD COLUMN IF NOT EXISTS searchable_{column_name} tsvector 
                GENERATED ALWAYS AS (to_tsvector('english', {column_name})) STORED;
                """
                },
            ).execute()

            # Create GIN index
            await self.supabase.rpc(
                "execute_sql",
                {
                    "query": f"""
                CREATE INDEX IF NOT EXISTS idx_{table_name}_{column_name}_search 
                ON {table_name} USING gin(searchable_{column_name});
                """
                },
            ).execute()

            return True
        except Exception as e:
            self._logger.error(f"Failed to create search index: {e}")
            return False

    async def _handle_connection_error(self, error: Exception) -> None:
        """Handle connection errors with retry logic"""

    async def _validate_connection(self) -> bool:
        """Validate connection is alive and reconnect if needed"""

    async def _execute_with_retry(self, operation: Callable) -> Any:
        """Execute operation with retry logic"""

    def _validate_batch_size(self, size: int) -> None:
        """Validate batch operation size"""

    async def _handle_transaction(self, operations: List[Callable]) -> Any:
        """Handle transaction operations"""

    @log_method()
    async def _execute_supabase_operation(
        self, operation_name: str, operation: Callable
    ) -> Any:
        """Execute a Supabase operation with retries."""
        max_retries = 3
        retry_count = 0

        while retry_count < max_retries:
            try:
                return await operation()
            except Exception as e:
                retry_count += 1
                if retry_count < max_retries:
                    self.logger.warning(
                        f"Retry {retry_count}/{max_retries} for {operation_name}"
                    )
                    await asyncio.sleep(2**retry_count)  # Exponential backoff
                else:
                    # Preserve the original error message
                    if isinstance(e, SupabaseQueryError):
                        raise e
                    raise SupabaseQueryError(f"{operation_name} failed: {str(e)}")

    def _log_operation_success(self, operation_name: str, start_time: datetime) -> None:
        """Log successful operation with timing."""
        duration = (datetime.now() - start_time).total_seconds()
        self._logger.info(f"{operation_name} completed in {duration:.2f}s")

    def _validate_table_name(self, table_name: str) -> None:
        """Validate table name."""
        if not isinstance(table_name, str) or not table_name.strip():
            raise SupabaseQueryError("Invalid table name")

    def _validate_batch_size(self, data: List[Any]) -> None:
        """Validate batch operation size."""
        if len(data) > self.MAX_BATCH_SIZE:
            raise SupabaseQueryError(
                "Batch size exceeded",
                details=f"Maximum batch size is {self.MAX_BATCH_SIZE}",
            )

    def _apply_filter(self, query, column: str, operator: FilterOperator, value: Any):
        """Apply a filter to the query based on operator type."""
        try:
            self._logger.debug(f"Applying filter: {column} {operator} {value}")
            self._logger.debug(f"Value type: {type(value)}")

            if not isinstance(column, str) or not column.strip():
                raise SupabaseQueryError("Invalid column name")

            if operator not in self.ALLOWED_OPERATORS:
                raise SupabaseQueryError(f"Unsupported filter operator: {operator}")

            # Use direct query methods instead of generic filter
            if operator == "eq":
                return query.eq(column, value)
            elif operator == "neq":
                return query.neq(column, value)
            elif operator == "lt":
                return query.lt(column, value)
            elif operator == "lte":
                return query.lte(column, value)
            elif operator == "gt":
                return query.gt(column, value)
            elif operator == "gte":
                return query.gte(column, value)
            elif operator == "like":
                return query.like(column, value)
            elif operator == "ilike":
                return query.ilike(column, value)
            elif operator == "is":
                return query.is_(column, value)
            elif operator == "in":
                return query.in_(column, value)
            elif operator == "contains":
                return query.contains(column, value)
            elif operator == "contained_by":
                return query.contained_by(column, value)
            elif operator == "text_search":
                return query.text_search(column, value)
            else:
                raise SupabaseQueryError(f"Unsupported operator: {operator}")

        except Exception as e:
            self._logger.error(
                f"Filter application failed: {column} {operator} {value}"
            )
            self._logger.error(f"Error details: {str(e)}")
            raise SupabaseQueryError(
                f"Failed to apply filter: {column} {operator} {value}", original_error=e
            )

    @log_method()
    async def get_table_constraints(self, table_name: str) -> dict:
        """Get table constraints including NOT NULL and CHECK constraints."""
        try:
            # Call our custom function using RPC
            result = await self.supabase.rpc(
                "get_table_info",  # Changed from get_table_constraints
                {"p_table_name": table_name},
            ).execute()

            if not result.data:
                self._logger.warning(f"No constraints found for table {table_name}")
                return {"not_null": [], "nullable": [], "check": []}

            # Extract all column names from the result
            all_columns = set()
            not_null_columns = set()
            check_constraints = []

            for row in result.data:
                column_name = row.get("column_name")
                if column_name:
                    all_columns.add(column_name)
                    if row.get("is_nullable") == "NO":
                        not_null_columns.add(column_name)
                if row.get("check_constraint"):
                    check_constraints.append(
                        {
                            "column": column_name,
                            "constraint": row.get("check_constraint"),
                        }
                    )

            constraints = {
                "not_null": list(not_null_columns),
                "nullable": list(all_columns - not_null_columns),
                "check": check_constraints,
            }

            self._logger.debug(
                f"Retrieved constraints for table {table_name}: {constraints}"
            )
            return constraints

        except Exception as e:
            self._logger.error(f"Error getting constraints: {str(e)}")
            raise SupabaseQueryError(f"Failed to get table constraints: {str(e)}")

    async def validate_select_against_constraints(
        self, table_name: str, fields: Dict[str, Any]
    ) -> None:
        """Validate that fields exist in the table schema.

        Args:
            table_name: Name of the table to validate against
            fields: Dictionary of fields to validate

        Raises:
            SupabaseQueryError: If any field doesn't exist in the table
        """
        try:
            constraints = await self.get_table_constraints(table_name)
            all_fields = set(
                constraints.get("not_null", []) + constraints.get("nullable", [])
            )

            invalid_fields = set(fields.keys()) - all_fields
            if invalid_fields:
                raise SupabaseQueryError(
                    f"Invalid fields for table {table_name}: {invalid_fields}"
                )
        except Exception as e:
            raise SupabaseQueryError(f"Field validation failed: {str(e)}")

    @log_method()
    async def select_from_table_basic(
        self,
        table_name: str,
        fields: Union[Literal["*"], List[str]],
        where_filters: Optional[
            List[Tuple[str, Literal["eq", "neq", "gt", "lt", ...], Any]]
        ] = None,
    ) -> List[Dict[str, Any]]:
        """A simplified version of select_from_table with basic options.

        Args:
            table_name: Name of the table to query
            fields: List of fields to select or "*" for all fields
            where_filters: Optional list of filters in format (column, operator, value)

        Returns:
            List[Dict[str, Any]]: Selected records

        Example:
            # Select specific fields with a filter
            records = await db.select_from_table_basic(
                "users",
                ["id", "name"],
                [("age", "gt", 18)]
            )

            # Select all fields
            all_records = await db.select_from_table_basic("users", "*")
        """
        try:
            return await self.select_from_table(
                table_name=table_name,
                fields=fields,
                where_filters=where_filters,
                limit=None,  # Use default (no limit)
                offset=None,  # Use default (no offset)
                order_by=None,  # Use default (no ordering)
                validate_constraints=False,  # Skip validation for simpler operation
            )
        except Exception as e:
            # Simplify error handling while preserving the original error
            raise SupabaseQueryError(
                f"Basic select operation failed: {str(e)}", original_error=e
            )

    @make_sync
    async def bulk_insert_sync(self, *args, **kwargs):
        return await self.bulk_insert(*args, **kwargs)

    @make_sync
    async def move_file_sync(self, *args, **kwargs):
        return await self.move_file(*args, **kwargs)

    @make_sync
    async def subscribe_to_channel_sync(self, *args, **kwargs):
        return await self.subscribe_to_channel(*args, **kwargs)

    @make_sync
    async def subscribe_to_table_sync(self, *args, **kwargs):
        return await self.subscribe_to_table(*args, **kwargs)

    # Sync versions of all async methods
    @make_sync
    async def select_from_table_sync(self, *args, **kwargs):
        return await self.select_from_table(*args, **kwargs)

    @make_sync
    async def update_table_sync(self, *args, **kwargs):
        return await self.update_table(*args, **kwargs)

    @make_sync
    async def insert_into_table_sync(self, *args, **kwargs):
        return await self.insert_into_table(*args, **kwargs)

    @make_sync
    async def delete_from_table_sync(self, *args, **kwargs):
        return await self.delete_from_table(*args, **kwargs)

    @make_sync
    async def login_sync(self, *args, **kwargs):
        return await self.login(*args, **kwargs)

    @make_sync
    async def logout_sync(self, *args, **kwargs):
        return await self.logout(*args, **kwargs)

    @make_sync
    async def reset_password_sync(self, *args, **kwargs):
        return await self.reset_password(*args, **kwargs)

    @make_sync
    async def signup_sync(self, *args, **kwargs):
        return await self.signup(*args, **kwargs)

    @make_sync
    async def get_user_sync(self, *args, **kwargs):
        return await self.get_user(*args, **kwargs)

    @make_sync
    async def set_current_domain_sync(self, *args, **kwargs):
        return await self.set_current_domain(*args, **kwargs)

    @make_sync
    async def upload_file_sync(self, *args, **kwargs):
        return await self.upload_file(*args, **kwargs)

    @make_sync
    async def download_file_sync(self, *args, **kwargs):
        return await self.download_file(*args, **kwargs)

    @make_sync
    async def delete_file_sync(self, *args, **kwargs):
        return await self.delete_file(*args, **kwargs)

    @make_sync
    async def list_files_sync(self, *args, **kwargs):
        return await self.list_files(*args, **kwargs)

    @make_sync
    async def login_with_provider_sync(self, *args, **kwargs):
        return await self.login_with_provider(*args, **kwargs)

    @make_sync
    async def refresh_session_sync(self, *args, **kwargs):
        return await self.refresh_session(*args, **kwargs)

    @make_sync
    async def update_user_sync(self, *args, **kwargs):
        return await self.update_user(*args, **kwargs)

    @make_sync
    async def get_user_roles_sync(self, *args, **kwargs):
        return await self.get_user_roles(*args, **kwargs)

    @make_sync
    async def check_permission_sync(self, *args, **kwargs):
        return await self.check_permission(*args, **kwargs)

    @make_sync
    async def create_bucket_sync(self, *args, **kwargs):
        return await self.create_bucket(*args, **kwargs)

    @make_sync
    async def get_bucket_sync(self, *args, **kwargs):
        return await self.get_bucket(*args, **kwargs)

    @make_sync
    async def list_buckets_sync(self, *args, **kwargs):
        return await self.list_buckets(*args, **kwargs)

    @make_sync
    async def delete_bucket_sync(self, *args, **kwargs):
        return await self.delete_bucket(*args, **kwargs)

    @make_sync
    async def empty_bucket_sync(self, *args, **kwargs):
        return await self.empty_bucket(*args, **kwargs)

    @make_sync
    async def rpc_sync(self, *args, **kwargs):
        return await self.rpc(*args, **kwargs)

    @make_sync
    async def update_password_sync(self, *args, **kwargs):
        return await self.update_password(*args, **kwargs)

    @make_sync
    async def verify_otp_sync(self, *args, **kwargs):
        return await self.verify_otp(*args, **kwargs)

    @make_sync
    async def set_session_sync(self, *args, **kwargs):
        return await self.set_session(*args, **kwargs)

    @make_sync
    async def create_search_index_sync(self, *args, **kwargs):
        return await self.create_search_index(*args, **kwargs)

    @make_sync
    async def cleanup_sync(self, *args, **kwargs):
        return await self.cleanup(*args, **kwargs)
