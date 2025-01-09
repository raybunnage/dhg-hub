from typing import Any, Callable, Dict, Optional
from ...core.base_logging import log_method
from ...core.exceptions import SupabaseError


class RealtimeMixin:
    """Mixin for realtime subscription operations."""

    @log_method()
    async def subscribe_to_table(
        self,
        table_name: str,
        callback: Callable[[Dict[str, Any]], None],
        event: str = "*",
        filter_str: Optional[str] = None,
    ) -> Any:
        """Subscribe to real-time changes on a table."""
        # ... existing subscribe_to_table implementation ...

    # Add other realtime methods
