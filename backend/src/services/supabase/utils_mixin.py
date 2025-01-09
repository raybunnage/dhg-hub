from typing import Any, Dict, List, Callable, Optional, Union
from datetime import datetime
import json
import hashlib
from .types import FilterOperator
from ...core.base_logging import log_method
from ...core.exceptions import SupabaseQueryError


class SupabaseUtilsMixin:
    """Mixin class containing utility methods for Supabase operations."""

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

    def _get_cache_key(self, table_name: str, update_fields: Dict[str, Any]) -> str:
        """Generate a cache key from table name and update fields."""
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

    def _log_operation_success(self, operation_name: str, start_time: datetime) -> None:
        """Log successful operation with timing."""
        duration = (datetime.now() - start_time).total_seconds()
        self._logger.info(f"{operation_name} completed in {duration:.2f}s")

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
