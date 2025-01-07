from typing import List, Optional, Dict, Any
from .base import SupabaseBase
from ...models.user import User


class SupabaseUser(SupabaseBase[User]):
    """User-specific Supabase operations."""

    def __init__(self, client):
        self.client = client
        self.table = "users"

    async def get_all(self) -> List[User]:
        response = self.client.table(self.table).select("*").execute()
        return [User.model_validate(user) for user in response.data]

    # Implement other abstract methods...
