from supabase import create_client, Client
from .config import get_settings


def get_supabase() -> Client:
    """Get Supabase client instance."""
    settings = get_settings()  # Get settings only when needed
    return create_client(settings.SUPABASE_URL, settings.SUPABASE_KEY)