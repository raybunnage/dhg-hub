from typing import Any, Callable, Dict, List, Union
from datetime import datetime, timedelta
from dhg.core.base_logging import log_method
from dhg.core.exceptions import SupabaseQueryError
import logging


class UtilsMixin:
    """Utility methods for Supabase service."""

    def __init__(self):
        """Initialize the mixin."""
        self._logger = logging.getLogger(self.__class__.__name__)
        self.supabase = None  # Will be set by the parent class

    @log_method()
    async def get_table_info(self, table_name: str) -> dict:
        """Get table information."""
        try:
            result = await self.supabase.rpc(
                "get_table_info", {"table_name": table_name}
            ).execute()
            return result.data
        except Exception as e:
            self._logger.error(f"Failed to get table info: {e}")
            raise SupabaseQueryError(f"Failed to get table info: {str(e)}")

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
