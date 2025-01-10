import pytest
from unittest.mock import Mock, AsyncMock
from dhg.db.experts import Experts


@pytest.fixture
def mock_supabase_client():
    """Create a mock Supabase client."""
    return Mock()


@pytest.fixture
def experts(mock_supabase_client):
    """Create Experts instance with mocked client."""
    return Experts(supabase_client=mock_supabase_client)


@pytest.mark.asyncio
async def test_get_expert(experts, mock_supabase_client):
    """Test getting a single expert."""
    # Setup mock response
    mock_response = Mock()
    mock_response.data = [{"id": "123", "name": "Test Expert"}]

    # Setup mock chain
    mock_execute = AsyncMock(return_value=mock_response)
    mock_eq = Mock()
    mock_eq.execute = mock_execute

    mock_select = Mock()
    mock_select.eq = Mock(return_value=mock_eq)

    mock_from = Mock()
    mock_from.select = Mock(return_value=mock_select)

    experts.client.from_ = Mock(return_value=mock_from)

    # Execute test
    result = await experts.get_expert("123")

    # Assert results
    assert result == {"id": "123", "name": "Test Expert"}
    experts.client.from_.assert_called_once_with("experts")


@pytest.mark.asyncio
async def test_list_experts(experts, mock_supabase_client):
    """Test listing all experts."""
    # Setup mock response
    mock_response = Mock()
    mock_response.data = [
        {"id": "123", "name": "Expert 1"},
        {"id": "456", "name": "Expert 2"},
    ]

    # Setup mock chain
    mock_execute = AsyncMock(return_value=mock_response)
    mock_select = Mock()
    mock_select.execute = mock_execute

    mock_from = Mock()
    mock_from.select = Mock(return_value=mock_select)

    experts.client.from_ = Mock(return_value=mock_from)

    # Execute test
    result = await experts.list_experts()

    # Assert results
    assert len(result) == 2
    assert result[0]["name"] == "Expert 1"
    assert result[1]["name"] == "Expert 2"
    experts.client.from_.assert_called_once_with("experts")
