import requests
import pytest
import time
from api_config import BASE_URL, get_cognito_headers

@pytest.mark.API
def test_post_trail_data_single():
    """
    Test POST /trail_data with a single data point.
    """
    url = f"{BASE_URL}/trail_data"
    headers = get_cognito_headers()
    
    # Generate unique timestamp for this test
    current_timestamp = int(time.time())
    device_id = "test_device_A"
    
    payload = {
        "trail_id": 1,
        "data": [
            {
                "device_id": device_id,
                "timestamp": current_timestamp,
                "battery": 95
            }
        ]
    }

    response = requests.post(url, json=payload, headers=headers)
    
    print(f"Response Status: {response.status_code}")
    print(f"Response Body: {response.json()}")
    
    assert response.status_code == 200
    response_data = response.json()
    assert "message" in response_data
    assert response_data["message"] == "Trail data uploaded"