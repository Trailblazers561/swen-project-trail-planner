import requests
import pytest

# Base URL of the API (replace with actual URL)
BASE_URL = "https://jsonplaceholder.typicode.com"

@pytest.mark.parametrize("endpoint, expected_status, payload", [
    ("/posts", 201, {"title": "foo", "body": "bar", "userId": 1}),
    ("/comments", 201, {"postId": 1, "name": "test", "email": "test@example.com", "body": "Nice post!"}),
])

@pytest.mark.API
def test_post_requests(endpoint, expected_status, payload):
    """Tests POST requests for various endpoints."""
    response = requests.post(BASE_URL + endpoint, json=payload)
    assert response.status_code == expected_status, f"Unexpected status code for {endpoint}: {response.status_code}"
    
    # Additional validation for successful responses
    if response.status_code == 201:
        response_data = response.json()
        assert "id" in response_data, f"Response for {endpoint} does not contain an 'id'"