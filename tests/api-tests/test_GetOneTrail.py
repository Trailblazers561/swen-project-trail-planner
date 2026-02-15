import requests
import pytest
from api_config import BASE_URL, get_cognito_headers

@pytest.mark.API
def test_get_trail_data_filtered():
    """
    Test GET /trail_data with query parameters to filter by specific trails.
    Updated to use correct query parameter name 'trails' (comma-separated) instead of 'trail'.
    """
    url = f"{BASE_URL}/trail_data"
    headers = get_cognito_headers()
    
    # Test with trails query parameter (comma-separated trail IDs)
    params = {
        "trails": "1,2",
        "start": "1731474000",
        "end": "1743700387"
    }
    
    response = requests.get(url, headers=headers, params=params)
    
    print(f"Response Status: {response.status_code}")
    print(f"Response Body: {response.json()}")
    
    assert response.status_code == 200
    response_data = response.json()
    # Response should be an array
    assert isinstance(response_data, list)
    
    # Verify all returned items are from the requested trails
    if len(response_data) > 0:
        for item in response_data:
            assert "trail_id" in item
            assert item["trail_id"] in [1, 2]  # Should only contain trail IDs 1 or 2
            assert "device_id" in item
            assert "timestamp" in item