from dhg.core.supabase_client import get_supabase


class SupabaseService:
    def __init__(self):
        self.client = get_supabase()

    async def get_user(self, user_id: str):
        response = (
            await self.client.from_("users").select("*").eq("id", user_id).execute()
        )
        return response.data[0] if response.data else None

    # Add other Supabase-related methods here
