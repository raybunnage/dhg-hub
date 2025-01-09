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

    # Add other utility methods
