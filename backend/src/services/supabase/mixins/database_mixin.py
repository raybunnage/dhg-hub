from typing import Any, Dict, List, Optional, Tuple, Union, Literal, Callable
from ...core.base_logging import log_method
from ...core.exceptions import SupabaseQueryError
from ..types import TableName, ColumnName, FilterOperator, InsertResult


class DatabaseMixin:
    """Mixin for database operations."""

    @log_method()
    async def select_from_table(
        self,
        table_name: str,
        fields: Union[Literal["*"], List[str]],
        where_filters: Optional[List[Tuple[str, FilterOperator, Any]]] = None,
        limit: Optional[int] = None,
        offset: Optional[int] = None,
        order_by: Optional[Dict[ColumnName, Literal["asc", "desc"]]] = None,
        validate_constraints: bool = False,
    ) -> List[Dict[str, Any]]:
        """Select records from a table with proper error handling."""
        # ... existing select_from_table implementation ...

    @log_method()
    async def insert_into_table(
        self,
        table_name: TableName,
        insert_fields: Union[Dict[ColumnName, Any], List[Dict[ColumnName, Any]]],
        upsert: bool = False,
        returning: str = "representation",
        ignore_duplicates: bool = False,
        validate_constraints: bool = False,
    ) -> InsertResult:
        """Insert records with proper error handling."""
        # ... existing insert_into_table implementation ...

    @log_method()
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

    def _apply_filter(self, query, column: str, operator: FilterOperator, value: Any):
        """Apply a filter to the query based on operator type."""
        try:
            if not isinstance(column, str) or not column.strip():
                raise SupabaseQueryError("Invalid column name")

            if operator not in self.ALLOWED_OPERATORS:
                raise SupabaseQueryError(f"Unsupported filter operator: {operator}")

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
            raise SupabaseQueryError(
                f"Failed to apply filter: {column} {operator} {value}", original_error=e
            )

    @log_method()
    async def get_table_constraints(self, table_name: str) -> dict:
        """Get table constraints including NOT NULL and CHECK constraints."""
        try:
            result = await self.supabase.rpc(
                "get_table_info",
                {"p_table_name": table_name},
            ).execute()

            if not result.data:
                return {"not_null": [], "nullable": [], "check": []}

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

            return {
                "not_null": list(not_null_columns),
                "nullable": list(all_columns - not_null_columns),
                "check": check_constraints,
            }

        except Exception as e:
            raise SupabaseQueryError(f"Failed to get table constraints: {str(e)}")

    def _validate_table_name(self, table_name: str) -> None:
        """Validate table name."""
        if not isinstance(table_name, str) or not table_name.strip():
            raise SupabaseQueryError("Invalid table name")

    def _validate_batch_size(self, size: int) -> None:
        """Validate batch operation size.

        Args:
            size: Size of the batch operation

        Raises:
            ValueError: If size exceeds MAX_BATCH_SIZE
        """
        if size > self.MAX_BATCH_SIZE:
            raise ValueError(
                f"Batch size {size} exceeds maximum allowed size of {self.MAX_BATCH_SIZE}"
            )

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

    @log_method()
    async def get_user_roles(
        self, user_id: Optional[str] = None
    ) -> List[Dict[str, Any]]:
        """Returns user roles with additional metadata
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

    # Add class constants at the top of the class
    ALLOWED_OPERATORS: List[FilterOperator] = [
        "eq",
        "neq",
        "gt",
        "gte",
        "lt",
        "lte",
        "like",
        "ilike",
        "is",
        "in",
        "contains",
        "contained_by",
        "text_search",
    ]
    MAX_BATCH_SIZE = 1000
