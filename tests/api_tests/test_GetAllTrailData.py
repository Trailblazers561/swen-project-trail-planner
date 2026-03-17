import requests
import pytest
from api_config import BASE_URL, get_cognito_headers

@pytest.mark.API
@pytest.mark.skip(reason="deprecated")
def test_get_all_trail_data():
    """
    Test GET /trail_data to retrieve all trail device logs.
    Updated to use correct endpoint path and query parameter format.
    """
    url = f"{BASE_URL}/trail_data"
    headers = get_cognito_headers()
    
    response = requests.get(url, headers=headers)
    
    print(f"Response Status: {response.status_code}")
    print(f"Response Body: {response.json()}")
    
    assert response.status_code == 200
    response_data = response.json()
    # Response should be an array of trail device log entries
    assert isinstance(response_data, list)
    
    # If there are items, verify they have the expected structure
    if len(response_data) > 0:
        item = response_data[0]
        assert "trail_id" in item
        assert "device_id" in item
        assert "timestamp" in item
