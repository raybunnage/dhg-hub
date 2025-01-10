from supabase import create_client, Client
from .config import settings


def get_supabase() -> Client:
    """Get Supabase client instance."""
    return create_client(settings.SUPABASE_URL, settings.SUPABASE_KEY)


supabase = get_supabase()
