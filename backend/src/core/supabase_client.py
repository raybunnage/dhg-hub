from supabase import create_client, Client
from .config import settings

def get_supabase() -> Client:
    return create_client(
        supabase_url=settings.supabase_url,
        supabase_key=settings.supabase_key
    )

supabase = get_supabase()
