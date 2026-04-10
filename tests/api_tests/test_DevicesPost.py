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

    payload = {
        "trail_id": 1,
        "name": "f1c9645dbc14efddc7d8a322685f26eb3c0b65c6d5aeb89f9a3a98a4f8f5c0d3",
        "battery": 95,
        "data": [
            {
                "ts": current_timestamp, "count": 123
            }
        ]
    }

    response = requests.put(url, json=payload, headers=headers)

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

    payload = {
        "name": "f1c9645dbc14efddc7d8a322685f26eb3c0b65c6d5aeb89f9a3a98a4f8f5c0d3",
        "battery": 96,
        "data": [
            {
                "ts": base_timestamp, "count": 412
            },
            {
                "ts": base_timestamp + 3600, "count": 12
            },
            {
                "ts": base_timestamp + 7200, "count": 322
            }
        ]
    }

    response = requests.put(url, json=payload, headers=headers)

    print(f"Response Status: {response.status_code}")
    print(f"Response Body: {response.json()}")

    assert response.status_code == 200
    response_data = response.json()
    assert "message" in response_data
    assert response_data["message"] == "Device data uploaded successfully"


@pytest.mark.API
@pytest.mark.skip(reason="deprecated") # Decivces cannot specify trail_id in their uploads
def test_post_device_data_with_additional_fields():
    """
    Test POST /devices with additional custom fields beyond required ones.
    """
    url = f"{BASE_URL}/devices"
    headers = get_api_key_headers()

    current_timestamp = int(time.time())

    payload = {
        "trail_id": 2,
        "name": "6ae48c0dcbd66a4d287f9cf05d2f2d2ff93a39b3dcd7db4a4f16279806b4f083",
        "battery": 88,
        "data": [
            {
                "ts": current_timestamp, "count": 42
            }
        ]
    }

    response = requests.put(url, json=payload, headers=headers)

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
        "name": "f1c9645dbc14efddc7d8a322685f26eb3c0b65c6d5aeb89f9a3a98a4f8f5c0d3",
        "battery": 90,
        "data": [
            {"ts": base_timestamp, "count": 132}
        ]
    }

    response_1 = requests.put(url, json=payload_1, headers=headers)
    assert response_1.status_code == 200

    payload_2 = {
        "trail_id": 2,
        "name": "6ae48c0dcbd66a4d287f9cf05d2f2d2ff93a39b3dcd7db4a4f16279806b4f083",
        "battery": 85,
        "data": [
            {"ts": base_timestamp, "count": 132}
        ]
    }

    response_2 = requests.put(url, json=payload_2, headers=headers)
    assert response_2.status_code == 200

    print(f"Device 1 Response: {response_1.json()}")
    print(f"Device 2 Response: {response_2.json()}")