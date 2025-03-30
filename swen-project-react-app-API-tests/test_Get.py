import requests
import pytest

# Base URL of the API (replace with actual URL)
BASE_URL = "https://yi7hc9zix0.execute-api.us-east-1.amazonaws.com/trailplanner_api_stage"

@pytest.mark.parametrize("endpoint, expected_status", [
    ("/posts/1", 200),
    ("/users/1", 200),
    ("/invalid-endpoint", 404),
])

@pytest.mark.API
def test_get_requests(endpoint, expected_status):
    """Tests GET requests for various endpoints."""
    response = requests.get(BASE_URL + endpoint)
    assert response.status_code == expected_status, f"Unexpected status code for {endpoint}: {response.status_code}"
    
    # Additional validation for successful responses
    if response.status_code == 200:
        assert response.json(), f"Empty response body for {endpoint}"