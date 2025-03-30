import requests
import pytest

# Base URL of the API (replace with actual URL)
BASE_URL = "https://yi7hc9zix0.execute-api.us-east-1.amazonaws.com/trailplanner_api_stage"

@pytest.mark.parametrize("endpoint, expected_status, payload", [
    ("/posts/1", 200, {"title": "updated title", "body": "updated body", "userId": 1}),
    ("/comments/1", 200, {"postId": 1, "name": "updated name", "email": "updated@example.com", "body": "Updated comment!"}),
])
def test_update_requests(endpoint, expected_status, payload):
    """Tests PUT requests for updating resources."""
    response = requests.put(BASE_URL + endpoint, json=payload)
    assert response.status_code == expected_status, f"Unexpected status code for {endpoint}: {response.status_code}"
    
    # Validate response content
    response_data = response.json()
    for key, value in payload.items():
        assert response_data.get(key) == value, f"Mismatch in updated field '{key}' for {endpoint}"