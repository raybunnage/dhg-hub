import pytest
from unittest.mock import Mock, patch
from dhg.core.supabase_client import get_supabase
from dhg.core.config import Settings


@pytest.fixture(autouse=True)
def mock_settings():
    """Mock settings with test values."""
    with patch("dhg.core.config.Settings") as MockSettings:
        # Create a mock settings instance
        settings_instance = Mock(spec=Settings)
        settings_instance.SUPABASE_URL = "http://test-url"
        settings_instance.SUPABASE_KEY = "test-key"

        # Make the Settings class return our mock instance
        MockSettings.return_value = settings_instance

        # Mock the get_settings function
        with patch("dhg.core.config.get_settings", return_value=settings_instance):
            yield settings_instance


@pytest.fixture
def mock_create_client():
    """Mock supabase create_client."""
    with patch("dhg.core.supabase_client.create_client") as mock:
        mock.return_value = Mock()
        yield mock


def test_get_supabase(mock_create_client, mock_settings):
    """Test that get_supabase creates client with correct settings."""
    client = get_supabase()

    # Verify create_client was called with correct arguments
    mock_create_client.assert_called_once_with(
        mock_settings.SUPABASE_URL, mock_settings.SUPABASE_KEY
    )

    assert client == mock_create_client.return_value
