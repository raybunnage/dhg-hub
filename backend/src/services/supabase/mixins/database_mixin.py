from typing import Any, Dict, List, Optional, Tuple, Union, Literal
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
    async def select_from_table_basic(
        self,
        table_name: str,
        fields: Union[Literal["*"], List[str]],
        where_filters: Optional[
            List[Tuple[str, Literal["eq", "neq", "gt", "lt", ...], Any]]
        ] = None,
    ) -> List[Dict[str, Any]]:
        """A simplified version of select_from_table with basic options."""
        try:
            return await self.select_from_table(
                table_name=table_name,
                fields=fields,
                where_filters=where_filters,
                limit=None,
                offset=None,
                order_by=None,
                validate_constraints=False,
            )
        except Exception as e:
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
        """Select data with a JOIN operation."""
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

    async def validate_select_against_constraints(
        self, table_name: str, fields: Dict[str, Any]
    ) -> None:
        """Validate that fields exist in the table schema."""
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
