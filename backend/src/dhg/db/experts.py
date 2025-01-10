from typing import Dict, Any, List, Optional
from dhg.core.base_logging import log_method


class Experts:
    """Experts database model."""

    def __init__(self, supabase_client=None):
        """Initialize with optional Supabase client."""
        self.client = supabase_client
        self.table_name = "experts"

    @log_method()
    async def get_expert(self, expert_id: str) -> Optional[Dict[str, Any]]:
        """Get expert by ID."""
        response = (
            await self.client.from_(self.table_name)
            .select("*")
            .eq("id", expert_id)
            .execute()
        )
        return response.data[0] if response.data else None

    @log_method()
    async def list_experts(self) -> List[Dict[str, Any]]:
        """List all experts."""
        response = await self.client.from_(self.table_name).select("*").execute()
        return response.data if response.data else []
