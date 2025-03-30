import requests
import pytest

# Base URL of the API (replace with actual URL)
BASE_URL = "https://jsonplaceholder.typicode.com"

@pytest.mark.parametrize("endpoint, expected_status", [
    ("/posts/1", 200),
    ("/comments/1", 200),
])
def test_delete_requests(endpoint, expected_status):
    """Tests DELETE requests for various endpoints."""
    response = requests.delete(BASE_URL + endpoint)
    assert response.status_code == expected_status, f"Unexpected status code for {endpoint}: {response.status_code}"
    
    # Validate empty response body for delete requests
    assert response.text == "", f"Response body for {endpoint} is not empty"