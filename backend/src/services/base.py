from typing import Any, Dict, List, Optional, TypeVar, Generic
from ..core.supabase_client import SupabaseClient

T = TypeVar('T')

class BaseService(Generic[T]):
    """Base service with common CRUD operations."""
    
    def __init__(self, table_name: str):
        self.client = SupabaseClient.get_client()
        self.table = table_name

    async def get_all(self) -> List[Dict[str, Any]]:
        """Get all records."""
        response = self.client.table(self.table).select("*").execute()
        return response.data

    async def get_by_id(self, id: str) -> Optional[Dict[str, Any]]:
        """Get record by ID."""
        response = self.client.table(self.table).select("*").eq("id", id).execute()
        return response.data[0] if response.data else None

    async def create(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Create a new record."""
        response = self.client.table(self.table).insert(data).execute()
        return response.data[0]

    async def update(self, id: str, data: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """Update a record."""
        response = self.client.table(self.table).update(data).eq("id", id).execute()
        return response.data[0] if response.data else None

    async def delete(self, id: str) -> bool:
        """Delete a record."""
        response = self.client.table(self.table).delete().eq("id", id).execute()
        return bool(response.data) 