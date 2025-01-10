from typing import Any, Callable, Dict, List, Union
from datetime import datetime, timedelta
from ...core.base_logging import log_method
from ...core.exceptions import SupabaseQueryError


class UtilsMixin:
    """Mixin for utility functions."""

    def _serialize_data(
        self, data: Union[Dict[str, Any], List[Dict[str, Any]]]
    ) -> Union[Dict[str, Any], List[Dict[str, Any]]]:
        """Serialize data for Supabase."""
        # ... existing _serialize_data implementation ...

    def _validate_table_name(self, table_name: str) -> None:
        """Validate table name."""
        # ... existing _validate_table_name implementation ...

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

    # Add other utility methods
