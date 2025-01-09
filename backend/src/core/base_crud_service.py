from abc import ABC, abstractmethod
from typing import Dict, Any, Optional, List, TypeVar, Generic, Tuple, Literal, Union
from pathlib import Path
import sys
import asyncio

project_root = str(Path(__file__).parent.parent.parent)
sys.path.append(project_root)

from src.services.supabase_service import (
    SupabaseService,
    TableName,
    ColumnName,
    WhereFilter,
    FilterOperator,
    ResponseRecord,
    InsertResult,
    SupabaseError,
    SupabaseQueryError,
    SupabaseConnectionError,
    SupabaseAuthenticationError,
    SupabaseAuthorizationError,
    SupabaseStorageError,
)
from src.services.base_logging import Logger
# from src.db.base_db import ValidationError, RecordNotFoundError, DatabaseError

T = TypeVar("T")
ReturnType = Literal["minimal", "representation"]


class CRUDInterface(ABC, Generic[T]):
    """Abstract interface defining standard CRUD operations matching Supabase service types."""

    @abstractmethod
    async def add(
        self,
        insert_fields: Union[Dict[ColumnName, Any], List[Dict[ColumnName, Any]]],
        upsert: bool = False,
        returning: ReturnType = "representation",
        ignore_duplicates: bool = False,
        validate_constraints: bool = False,
    ) -> Optional[InsertResult]:
        """Create a new record matching Supabase insert_into_table signature."""
        pass

    @abstractmethod
    async def get_by_id(
        self, id: str, fields: Optional[Union[Literal["*"], List[ColumnName]]] = None
    ) -> Optional[ResponseRecord]:
        """Retrieve a record by ID matching Supabase select_from_table signature."""
        pass

    @abstractmethod
    async def get_all(
        self,
        fields: Union[Literal["*"], List[ColumnName]],
        where_filters: Optional[List[WhereFilter]] = None,
        limit: Optional[int] = None,
        offset: Optional[int] = None,
        order_by: Optional[Dict[ColumnName, Literal["asc", "desc"]]] = None,
    ) -> Optional[List[ResponseRecord]]:
        """Retrieve all records matching Supabase select_from_table signature."""
        pass

    @abstractmethod
    async def update(
        self,
        id: str,
        update_fields: Dict[ColumnName, Any],
        where_filters: Optional[List[WhereFilter]] = None,
    ) -> Optional[ResponseRecord]:
        """Update a record matching Supabase update_table signature."""
        pass

    @abstractmethod
    async def delete(
        self,
        id: str,
        where_filters: Optional[List[WhereFilter]] = None,
        returning: ReturnType = "representation",
    ) -> Optional[List[ResponseRecord]]:
        """Delete a record matching Supabase delete_from_table signature."""
        pass


class BaseCRUDService(CRUDInterface[T]):
    """Base implementation of CRUD operations using Supabase."""

    async def _initialize_session(
        self, email: str, password: str, domain_id: str
    ) -> None:
        """Initialize authenticated session and set domain."""
        try:
            # Attempt login
            login_success = await self.supabase.login(email, password)
            if not login_success:
                raise SupabaseAuthenticationError(
                    "Failed to login with provided credentials"
                )

            # Set current domain
            await self.supabase.set_current_domain(domain_id)
            self.logger.debug(
                f"Successfully initialized session with domain {domain_id}"
            )

        except Exception as e:
            self.logger.error(f"Session initialization failed: {str(e)}")
            raise

    def __init__(
        self,
        supabase_client: SupabaseService,
        table_name: TableName,
        email: str = None,
        password: str = None,
        domain_id: str = None,
    ):
        """Initialize with typed table name and optional auth credentials."""
        self.supabase = supabase_client
        self.table_name = table_name
        self.logger = Logger(self.__class__.__name__)

        # If credentials are provided, initialize session
        if email and password and domain_id:
            try:
                # Try to get the current event loop
                loop = asyncio.get_event_loop()
                if loop.is_running():
                    # If loop is running, create a new task instead
                    loop.create_task(
                        self._initialize_session(email, password, domain_id)
                    )
                else:
                    # If no loop is running, we can run until complete
                    loop.run_until_complete(
                        self._initialize_session(email, password, domain_id)
                    )
            except RuntimeError:
                # If no event loop exists in thread, create new one
                loop = asyncio.new_event_loop()
                asyncio.set_event_loop(loop)
                loop.run_until_complete(
                    self._initialize_session(email, password, domain_id)
                )

        self.parent_id_column = "id"  # Default column name for the parent table's ID
        self.alias_parent_id_column = (
            "expert_uuid"  # Default foreign key column in alias table
        )

    async def _validate_data(self, data: Dict[str, Any]) -> bool:
        """
        Validate data before operations. Override this in child classes.
        Returns True if valid, raises ValidationError if invalid.
        """
        return True

    async def _handle_db_operation(self, operation_name: str, operation):
        """Handle database operations with proper error handling."""
        try:
            return await operation()
        except Exception as e:
            self.logger.error(f"Error in {operation_name}: {str(e)}")
            raise

    async def add(
        self,
        insert_fields: Union[Dict[ColumnName, Any], List[Dict[ColumnName, Any]]],
        upsert: bool = False,
        returning: ReturnType = "representation",
        ignore_duplicates: bool = False,
        validate_constraints: bool = True,
    ) -> Optional[InsertResult]:
        """Create a new record with proper validation."""
        self.logger.debug(f"Adding record to {self.table_name}: {insert_fields}")

        async def _add_operation():
            # Validate data
            if isinstance(insert_fields, dict):
                await self._validate_data(insert_fields)
            else:
                for fields in insert_fields:
                    await self._validate_data(fields)

            # Insert new record(s)
            result = await self.supabase.insert_into_table(
                self.table_name,
                insert_fields,
                upsert=upsert,
                returning=returning,
                ignore_duplicates=ignore_duplicates,
                validate_constraints=validate_constraints,
            )
            if not result:
                raise SupabaseQueryError(f"Failed to add record to {self.table_name}")
            return result

        return await self._handle_db_operation("add", _add_operation)

    async def get_by_id(
        self, id: str, fields: Optional[Union[Literal["*"], List[ColumnName]]] = None
    ) -> Optional[ResponseRecord]:
        """Retrieve a record by ID."""
        self.logger.debug(f"Getting record by ID from {self.table_name}: {id}")

        async def _get_by_id_operation():
            result = await self.supabase.select_from_table(
                self.table_name, fields or ["*"], [("id", "eq", id)]
            )
            if not result:
                raise SupabaseQueryError(f"Record not found in {self.table_name}: {id}")
            return result[0]

        return await self._handle_db_operation("get_by_id", _get_by_id_operation)

    async def get_all(
        self,
        fields: Union[Literal["*"], List[ColumnName]],
        where_filters: Optional[List[WhereFilter]] = None,
        limit: Optional[int] = None,
        offset: Optional[int] = None,
        order_by: Optional[Dict[ColumnName, Literal["asc", "desc"]]] = None,
        validate_constraints: bool = True,
    ) -> Optional[List[ResponseRecord]]:
        """Retrieve all records with optional filters and pagination."""
        self.logger.debug(f"Getting all records from {self.table_name}")

        async def _get_all_operation():
            result = await self.supabase.select_from_table(
                self.table_name,
                fields,
                where_filters,
                limit=limit,
                offset=offset,
                order_by=order_by,
                validate_constraints=validate_constraints,
            )
            if not result:
                raise SupabaseQueryError(f"No records found in {self.table_name}")
            return result

        return await self._handle_db_operation("get_all", _get_all_operation)

    async def update(
        self,
        id: str,
        update_fields: Dict[ColumnName, Any],
        where_filters: Optional[List[WhereFilter]] = None,
        validate_constraints: bool = True,
    ) -> Optional[ResponseRecord]:
        """Update a record with validation."""
        self.logger.debug(f"Updating record in {self.table_name}: {id}")

        async def _update_operation():
            # Verify record exists
            existing = await self.get_by_id(id)
            if not existing:
                raise SupabaseQueryError(f"Record not found in {self.table_name}: {id}")

            # Validate update data
            await self._validate_data({**existing, **update_fields})

            # Combine ID filter with additional filters
            filters = [("id", "eq", id)]
            if where_filters:
                filters.extend(where_filters)

            # Perform update
            result = await self.supabase.update_table(
                self.table_name,
                update_fields,
                filters,
                validate_constraints=validate_constraints,
            )
            if not result:
                raise SupabaseQueryError(
                    f"Failed to update record in {self.table_name}"
                )

            return result

        return await self._handle_db_operation("update", _update_operation)

    async def delete(
        self,
        id: str,
        where_filters: Optional[List[WhereFilter]] = None,
        returning: ReturnType = "representation",
    ) -> Optional[List[ResponseRecord]]:
        """Delete a record."""
        self.logger.debug(f"Deleting record from {self.table_name}: {id}")

        async def _delete_operation():
            # Verify record exists
            existing = await self.get_by_id(id)
            if not existing:
                raise SupabaseQueryError(f"Record not found in {self.table_name}: {id}")

            # Combine ID filter with additional filters
            filters = [("id", "eq", id)]
            if where_filters:
                filters.extend(where_filters)

            result = await self.supabase.delete_from_table(
                self.table_name, filters, returning=returning
            )
            return result

        return await self._handle_db_operation("delete", _delete_operation)

    async def get_aliases(
        self, parent_id: str, alias_table: str, parent_id_column: str = None
    ) -> Optional[List[ResponseRecord]]:
        """Get aliases for a record.

        Args:
            parent_id: ID of the parent record
            alias_table: Name of the alias table
            parent_id_column: Name of the foreign key column in the alias table (defaults to self.alias_parent_id_column)
        """
        parent_id_col = parent_id_column or self.alias_parent_id_column
        return await self.supabase.select_from_table(
            alias_table, ["*"], [(parent_id_col, "eq", parent_id)]
        )

    async def add_alias(
        self,
        parent_id: str,
        alias_name: str,
        alias_table: str,
        parent_id_column: str = None,
    ) -> Optional[ResponseRecord]:
        """Add an alias for a record.

        Args:
            parent_id: ID of the parent record
            alias_name: Name of the alias
            alias_table: Name of the alias table
            parent_id_column: Name of the foreign key column in the alias table (defaults to self.alias_parent_id_column)
        """
        parent_id_col = parent_id_column or self.alias_parent_id_column

        async def _add_alias_operation():
            # Check for existing alias
            existing_alias = await self.supabase.select_from_table(
                alias_table,
                ["id"],
                [
                    (parent_id_col, "eq", parent_id),
                    ("alias_name", "eq", alias_name),
                ],
            )
            if existing_alias:
                raise SupabaseQueryError(f"Alias already exists: {alias_name}")

            # Add new alias
            result = await self.supabase.insert_into_table(
                alias_table,
                {
                    parent_id_col: parent_id,
                    "alias_name": alias_name,
                },
            )
            if not result:
                raise SupabaseQueryError(f"Failed to add alias: {alias_name}")
            return result

        return await self._handle_db_operation("add alias", _add_alias_operation)

    async def delete_alias(
        self,
        alias_id: str,
        alias_table: TableName,
    ) -> bool:
        """Delete an alias record.

        Args:
            alias_id: The ID of the alias to delete
            alias_table: Name of the alias table

        Returns:
            bool: True if deletion was successful
        """
        if not alias_id:
            raise SupabaseQueryError("alias_id is required")

        async def _delete_alias_operation():
            # Verify alias exists
            existing_alias = await self.supabase.select_from_table(
                alias_table, ["id"], [("id", "eq", alias_id)]
            )

            if not existing_alias:
                raise SupabaseQueryError(f"Alias not found: {alias_id}")

            result = await self.supabase.delete_from_table(
                alias_table, [("id", "eq", alias_id)]
            )
            if not result:
                raise SupabaseQueryError(f"Failed to delete alias: {alias_id}")
            return True

        return await self._handle_db_operation("delete alias", _delete_alias_operation)
