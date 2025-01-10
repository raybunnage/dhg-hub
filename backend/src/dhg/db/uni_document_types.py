from typing import Dict, Any, List, Optional
from dhg.core.base_logging import log_method


class UniDocumentTypes:
    """University document types model."""

    def __init__(self, supabase_client=None):
        self.client = supabase_client
        self.table_name = "uni_document_types"

    @log_method()
    async def get_document_type(self, type_id: str) -> Optional[Dict[str, Any]]:
        """Get document type by ID."""
        response = (
            await self.client.from_(self.table_name)
            .select("*")
            .eq("id", type_id)
            .execute()
        )
        return response.data[0] if response.data else None

    @log_method()
    async def list_document_types(self) -> List[Dict[str, Any]]:
        """List all document types."""
        response = await self.client.from_(self.table_name).select("*").execute()
        return response.data if response.data else []
