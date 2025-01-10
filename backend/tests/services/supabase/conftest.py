import pytest
from unittest.mock import Mock, AsyncMock


@pytest.fixture
def mock_supabase_client():
    """Create a mock Supabase client with common attributes."""
    client = Mock()
    client.auth = AsyncMock()
    client.from_ = Mock()
    client.storage = AsyncMock()
    return client


@pytest.fixture
def mock_logger():
    """Create a mock logger."""
    return Mock()
