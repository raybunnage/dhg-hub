import pytest
from unittest.mock import patch
from dhg.core.supabase_client import get_supabase
from dhg.core.config import TestConfig


@pytest.fixture
def mock_settings():
    """Mock settings for testing."""
    return TestConfig()


@pytest.fixture
def mock_supabase_client():
    """Mock Supabase client."""
    with patch("dhg.core.supabase_client.create_client") as mock_create:
        mock_client = mock_create.return_value
        yield mock_client


def test_get_supabase(mock_settings, mock_supabase_client):
    """Test getting Supabase client."""
    with patch("dhg.core.supabase_client.get_settings", return_value=mock_settings):
        client = get_supabase()
        assert client == mock_supabase_client
