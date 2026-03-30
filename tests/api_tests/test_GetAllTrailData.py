import requests
import pytest
from api_config import BASE_URL, get_cognito_headers

@pytest.mark.API
def test_get_all_trail_data():
    """
    Test GET /trail_data to retrieve all trail device logs.
    Updated to use correct endpoint path and query parameter format.
    """
    url = f"{BASE_URL}/trail_data"
    headers = get_cognito_headers()
    params = {
        "trail_id": [1,2,3,4,5,6,7,8,9,10],
        "start": "2026-01-01",
        "end": "2026-12-31"
    }
    
    response = requests.get(url, headers=headers, params=params)
    
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
        assert "device_trail_id" in item
        assert "start" in item
        assert "count" in item
        assert "battery" in item