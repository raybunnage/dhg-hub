import pytest
from src.core.supabase_client import SupabaseClient


def test_supabase_client_singleton():
    client1 = SupabaseClient.get_client()
    client2 = SupabaseClient.get_client()
    assert client1 is client2
