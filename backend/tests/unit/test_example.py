def test_home_page(client):
    """Test the home page."""
    response = client.get("/")
    assert response.status_code == 200
    # Add more assertions as needed
