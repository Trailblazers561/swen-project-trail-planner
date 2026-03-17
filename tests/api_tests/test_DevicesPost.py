import requests
import pytest
import time
from api_config import BASE_URL, get_api_key_headers

@pytest.mark.API
def test_post_device_data_success():
    """
    Test POST /devices.
    """
    url = f"{BASE_URL}/devices"
    headers = get_api_key_headers()

    current_timestamp = int(time.time())
    device_id = "deviceA"

    payload = {
        "trail_id": 1,
        "device_id": device_id,
        "battery": 95,
        "data": [
            {
                "ts": current_timestamp
            }
        ]
    }

    response = requests.post(url, json=payload, headers=headers)

    print(f"Response Status: {response.status_code}")
    print(f"Response Body: {response.json()}")

    assert response.status_code == 200
    response_data = response.json()
    assert "message" in response_data
    assert response_data["message"] == "Device data uploaded successfully"


@pytest.mark.API
def test_post_device_data_batch_payload():
    """
    Test POST /devices with a batch payload containing multiple readings.
    """
    url = f"{BASE_URL}/devices"
    headers = get_api_key_headers()

    base_timestamp = int(time.time())
    device_id = "deviceB"

    payload = {
        "device_id": device_id,
        "battery": 96,
        "data": [
            {
                "ts": base_timestamp,
            },
            {
                "ts": base_timestamp + 1,
            },
            {
                "ts": base_timestamp + 2,
            }
        ]
    }

    response = requests.post(url, json=payload, headers=headers)

    print(f"Response Status: {response.status_code}")
    print(f"Response Body: {response.json()}")

    assert response.status_code == 200
    response_data = response.json()
    assert "message" in response_data
    assert response_data["message"] == "Device data uploaded successfully"


@pytest.mark.API
def test_post_device_data_with_additional_fields():
    """
    Test POST /devices with additional custom fields beyond required ones.
    """
    url = f"{BASE_URL}/devices"
    headers = get_api_key_headers()

    current_timestamp = int(time.time())
    device_id = "deviceC"

    payload = {
        "trail_id": 2,
        "device_id": device_id,
        "battery": 88,
        "data": [
            {
                "ts": current_timestamp,
            }
        ]
    }

    response = requests.post(url, json=payload, headers=headers)

    print(f"Response Status: {response.status_code}")
    print(f"Response Body: {response.json()}")

    assert response.status_code == 200
    response_data = response.json()
    assert "message" in response_data
    assert response_data["message"] == "Device data uploaded successfully"


@pytest.mark.API
def test_post_device_data_multiple_devices():
    """
    Test POST /devices with multiple sequential requests from different devices.
    """
    url = f"{BASE_URL}/devices"
    headers = get_api_key_headers()

    base_timestamp = int(time.time())

    payload_1 = {
        "trail_id": 1,
        "device_id": "deviceD",
        "battery": 90,
        "data": [
            {"ts": base_timestamp}
        ]
    }

    response_1 = requests.post(url, json=payload_1, headers=headers)
    assert response_1.status_code == 200

    payload_2 = {
        "trail_id": 2,
        "device_id": "deviceE",
        "battery": 85,
        "data": [
            {"ts": base_timestamp + 1}
        ]
    }

    response_2 = requests.post(url, json=payload_2, headers=headers)
    assert response_2.status_code == 200

    print(f"Device 1 Response: {response_1.json()}")
    print(f"Device 2 Response: {response_2.json()}")

