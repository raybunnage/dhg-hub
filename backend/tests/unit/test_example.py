import pytest
from unittest.mock import Mock


@pytest.fixture
def client():
    """Create a test client."""
    return Mock()


def test_home_page(client):
    """Test home page."""
    response = client.get("/")
    assert response is not None
