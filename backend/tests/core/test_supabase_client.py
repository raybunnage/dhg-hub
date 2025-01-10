import pytest
from unittest.mock import patch
from dhg.core.supabase_client import get_supabase


def test_get_supabase():
    """Test that get_supabase returns a client."""
    with patch("dhg.core.supabase_client.create_client") as mock_create:
        get_supabase()
        mock_create.assert_called_once()
