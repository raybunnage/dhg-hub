import pytest
from unittest.mock import Mock, AsyncMock, patch
from hypothesis import given, strategies as st, settings
from hypothesis import HealthCheck
from dhg.services.supabase.service import SupabaseService


@pytest.fixture
def mock_response():
    """Create a mock response with data."""
    response = Mock()
    response.data = [{"id": "123", "name": "Test User"}]
    return response


@pytest.fixture
def mock_supabase_client(mock_response):
    """Create a mock Supabase client with async support."""
    client = Mock()

    # Create mock execute function that returns an awaitable
    mock_execute = AsyncMock(return_value=mock_response)
    mock_eq = Mock()
    mock_eq.execute = mock_execute

    mock_select = Mock()
    mock_select.eq = Mock(return_value=mock_eq)

    mock_table = Mock()
    mock_table.select = Mock(return_value=mock_select)

    # Reset the from_ mock for each test
    client.from_ = Mock(return_value=mock_table)

    return client


@pytest.fixture(scope="function")
def service(mock_supabase_client):
    """Create a SupabaseService with mocked client."""
    return SupabaseService(
        url="https://example.supabase.co",
        key="test-key",
        client=mock_supabase_client,  # Pass client directly
    )


@given(user_id=st.text(min_size=1))
@settings(suppress_health_check=[HealthCheck.function_scoped_fixture])
@pytest.mark.asyncio
async def test_get_user_integration(user_id, service, mock_response):
    """Test get_user with hypothesis generated data."""
    # Update mock response data with generated user_id
    mock_response.data = [{"id": user_id, "name": "Test User"}]

    # Reset the from_ mock before the test
    service.client.from_.reset_mock()

    # Execute test
    result = await service.get_user(user_id)

    # Assert results
    assert result == {"id": user_id, "name": "Test User"}
    service.client.from_.assert_called_once_with("users")
