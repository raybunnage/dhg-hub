import pytest
from unittest.mock import Mock, AsyncMock, patch
from dhg.services.supabase.service import SupabaseService
from dhg.core.exceptions import (
    SupabaseOperationalError,
    UserNotFoundError,
    InvalidCredentialsError,
)


@pytest.fixture
def mock_supabase_client():
    """Create a mock Supabase client."""
    mock_client = Mock()
    return mock_client


@pytest.fixture
def service(monkeypatch, mock_supabase_client):
    """Create a SupabaseService with mocked client."""
    monkeypatch.setattr(
        "dhg.core.supabase_client.create_client", lambda url, key: mock_supabase_client
    )
    return SupabaseService()


def test_supabase_service_init(service, mock_supabase_client):
    """Test SupabaseService initialization with mocked dependencies."""
    assert service is not None
    assert service.client == mock_supabase_client


@pytest.mark.asyncio
async def test_get_user_success(service, mock_supabase_client):
    """Test successful get_user method."""
    # Setup mock response
    mock_response = Mock()
    mock_response.data = [{"id": "123", "name": "Test User"}]

    # Setup mock chain
    mock_execute = AsyncMock(return_value=mock_response)
    mock_eq = Mock()
    mock_eq.execute = mock_execute

    mock_select = Mock()
    mock_select.eq = Mock(return_value=mock_eq)

    mock_from = Mock()
    mock_from.select = Mock(return_value=mock_select)

    service.client.from_ = Mock(return_value=mock_from)

    # Execute test
    result = await service.get_user("123")

    # Assert results
    assert result == {"id": "123", "name": "Test User"}
    service.client.from_.assert_called_once_with("users")


@pytest.mark.asyncio
async def test_get_user_not_found(service, mock_supabase_client):
    """Test get_user method when user is not found."""
    # Setup mock response with no data
    mock_response = Mock()
    mock_response.data = []

    # Create a complete mock chain
    mock_execute = AsyncMock(return_value=mock_response)
    mock_eq = Mock()
    mock_eq.execute = mock_execute

    mock_select = Mock()
    mock_select.eq = Mock(return_value=mock_eq)

    mock_from = Mock()
    mock_from.select = Mock(return_value=mock_select)

    # Set up the complete chain
    service.client.from_ = Mock(return_value=mock_from)
    mock_from.select.return_value = mock_select
    mock_select.eq.return_value = mock_eq

    # Execute test and check for exception
    with pytest.raises(UserNotFoundError) as exc_info:
        await service.get_user("123")

    assert "User 123 not found" in str(exc_info.value)

    # Verify the mock chain was called correctly
    service.client.from_.assert_called_once_with("users")
    mock_from.select.assert_called_once_with("*")
    mock_select.eq.assert_called_once_with("id", "123")
    mock_execute.assert_called_once()


@pytest.mark.asyncio
async def test_get_user_error(service, mock_supabase_client):
    """Test get_user method when an error occurs."""
    # Setup mock to raise an exception
    service.client.from_ = Mock(side_effect=Exception("Test error"))

    # Execute test and check for exception
    with pytest.raises(SupabaseOperationalError) as exc_info:
        await service.get_user("123")

    assert "Failed to get user" in str(exc_info.value)
