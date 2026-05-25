import requests
import pytest
import time
from config import BASE_URL, get_cognito_headers

@pytest.mark.API
def test_post_trail_data_multiple():
    """
    Test POST /trail_data with multiple data points in a batch.
    """
    url = f"{BASE_URL}/trail_data"
    headers = get_cognito_headers()
    
    # Generate unique timestamps for this test
    base_timestamp = int(time.time())
    device_id = "test_device_B"
    
    payload = {
        "trail_id": 1,
        "data": [
            {
                "device_id": device_id,
                "timestamp": base_timestamp,
                "battery": 95
            },
            {
                "device_id": device_id,
                "timestamp": base_timestamp + 1,
                "battery": 94
            },
            {
                "device_id": device_id,
                "timestamp": base_timestamp + 2,
                "battery": 93
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