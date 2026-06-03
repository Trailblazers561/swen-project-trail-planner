import requests
import pytest
import time
from api_config import BASE_URL, get_api_key_headers

@pytest.mark.API
@pytest.mark.skip(reason="temp_until_moved_off_public_api")
def test_post_device_data_missing_api_key():
    """
    Test POST /devices without API key - should return 403 Forbidden.
    """
    url = f"{BASE_URL}/devices"
    headers = {
        "Content-Type": "application/json"
        # Missing X-Api-Key header
    }
    
    current_timestamp = int(time.time())
    payload = {
        "trail_id": 1,
        "name": "f1c9645dbc14efddc7d8a322685f26eb3c0b65c6d5aeb89f9a3a98a4f8f5c0d3",
        "battery": 94,
        "data": [
            {"ts": current_timestamp, "count": 21}
        ]
    }

    response = requests.put(url, json=payload, headers=headers)
    
    print(f"Response Status: {response.status_code}")
    print(f"Response Body: {response.text}")
    
    assert response.status_code == 403


@pytest.mark.API
@pytest.mark.skip(reason="temp_until_moved_off_public_api")
def test_post_device_data_invalid_api_key():
    """
    Test POST /devices with invalid API key - should return 403 Forbidden.
    """
    url = f"{BASE_URL}/devices"
    headers = {
        "X-Api-Key": "INVALID-API-KEY",
        "Content-Type": "application/json"
    }
    
    current_timestamp = int(time.time())
    payload = {
        "trail_id": 1,
        "name": "f1c9645dbc14efddc7d8a322685f26eb3c0b65c6d5aeb89f9a3a98a4f8f5c0d3",
        "battery": 94,
        "data": [
            {"ts": current_timestamp, "count": 422}
        ]
    }

    response = requests.put(url, json=payload, headers=headers)
    
    print(f"Response Status: {response.status_code}")
    print(f"Response Body: {response.text}")
    
    assert response.status_code == 403


@pytest.mark.API
def test_post_device_data_missing_device_id():
    """
    Test POST /devices with missing required field device_id - should return 400 Bad Request.
    """
    url = f"{BASE_URL}/devices"
    headers = get_api_key_headers()

    payload = {
        "trail_id": 1,
        "battery": 95,
        "data": [
            {"ts": int(time.time()), "count": 74}
        ]
    }

    response = requests.put(url, json=payload, headers=headers)

    print(f"Response Status: {response.status_code}")
    print(f"Response Body: {response.json()}")

    assert response.status_code == 400
    response_data = response.json()
    assert "error" in response_data
    assert "name" in response_data["error"]


@pytest.mark.API
def test_post_device_data_missing_data_array():
    """
    Test POST /devices with missing data array - should return 400 Bad Request.
    """
    url = f"{BASE_URL}/devices"
    headers = get_api_key_headers()

    payload = {
        "trail_id": 1,
        "name": "f1c9645dbc14efddc7d8a322685f26eb3c0b65c6d5aeb89f9a3a98a4f8f5c0d3",
        "battery": 92
    }

    response = requests.put(url, json=payload, headers=headers)

    print(f"Response Status: {response.status_code}")
    print(f"Response Body: {response.json()}")

    assert response.status_code == 400
    response_data = response.json()
    assert "data" in response_data["error"]


@pytest.mark.API
def test_post_device_data_empty_data_array():
    """
    Test POST /devices with empty data array - should return 400 Bad Request.
    """
    url = f"{BASE_URL}/devices"
    headers = get_api_key_headers()

    payload = {
        "trail_id": 1,
        "name": "f1c9645dbc14efddc7d8a322685f26eb3c0b65c6d5aeb89f9a3a98a4f8f5c0d3",
        "data": []
    }

    response = requests.put(url, json=payload, headers=headers)

    print(f"Response Status: {response.status_code}")
    print(f"Response Body: {response.json()}")

    assert response.status_code == 400
    response_data = response.json()
    assert "data_points" in response_data["error"]


@pytest.mark.API
def test_post_device_data_missing_timestamp_in_entry():
    """
    Test POST /devices with missing ts in a data entry - should return 400 Bad Request.
    """
    url = f"{BASE_URL}/devices"
    headers = get_api_key_headers()

    payload = {
        "trail_id": 1,
        "name": "f1c9645dbc14efddc7d8a322685f26eb3c0b65c6d5aeb89f9a3a98a4f8f5c0d3",
        "data": [
            {}
        ]
    }

    response = requests.put(url, json=payload, headers=headers)

    print(f"Response Status: {response.status_code}")
    print(f"Response Body: {response.json()}")

    assert response.status_code == 400
    response_data = response.json()
    assert "ts" in response_data["error"]


@pytest.mark.API
@pytest.mark.skip(reason="deprecated") # No more trail id override
def test_post_device_data_invalid_trail_id_override():
    """
    Test POST /devices with invalid trail_id override - should return 400 Bad Request.
    """
    url = f"{BASE_URL}/devices"
    headers = get_api_key_headers()

    payload = {
        "name": "f1c9645dbc14efddc7d8a322685f26eb3c0b65c6d5aeb89f9a3a98a4f8f5c0d3",
        "trail_id": "not-an-int",
        "data": [
            {"ts": int(time.time()), "count": 93}
        ]
    }

    response = requests.put(url, json=payload, headers=headers)

    print(f"Response Status: {response.status_code}")
    print(f"Response Body: {response.json()}")

    assert response.status_code == 400
    response_data = response.json()
    assert "trail_id" in response_data["error"]


@pytest.mark.API
def test_post_device_data_invalid_timestamp_type():
    """
    Test POST /devices with invalid timestamp type - should return 400 Bad Request.
    """
    url = f"{BASE_URL}/devices"
    headers = get_api_key_headers()

    payload = {
        "trail_id": 1,
        "name": "f1c9645dbc14efddc7d8a322685f26eb3c0b65c6d5aeb89f9a3a98a4f8f5c0d3",
        "data": [
            {"ts": "not-a-number", "count": 12}
        ],
        "battery": 87
    }

    response = requests.put(url, json=payload, headers=headers)

    print(f"Response Status: {response.status_code}")
    print(f"Response Body: {response.json()}")

    assert response.status_code == 400
    response_data = response.json()
    assert "timestamp" in response_data["error"].lower()


@pytest.mark.API
def test_post_device_data_empty_body():
    """
    Test POST /devices with empty request body - should return 400 Bad Request.
    """
    url = f"{BASE_URL}/devices"
    headers = get_api_key_headers()
    
    payload = {}

    response = requests.put(url, json=payload, headers=headers)
    
    print(f"Response Status: {response.status_code}")
    print(f"Response Body: {response.json()}")
    
    assert response.status_code == 400
    response_data = response.json()
    assert "error" in response_data


@pytest.mark.API
def test_post_device_data_duplicate_timestamps():
    """
    Test POST /devices with duplicate timestamps from the same device.
    Duplicate timestamps should be silently ignored and the request should succeed.
    """
    url = f"{BASE_URL}/devices"
    headers = get_api_key_headers()
    
    current_timestamp = int(time.time())
    device_id = "deviceDuplicateTest"

    payload = {
        "trail_id": 1,
        "name": "f1c9645dbc14efddc7d8a322685f26eb3c0b65c6d5aeb89f9a3a98a4f8f5c0d3",
        "battery": 90,
        "data": [
            {"ts": current_timestamp, "count": 32},
            {"ts": current_timestamp, "count": 32},
            {"ts": current_timestamp + 1, "count": 32},
            {"ts": current_timestamp, "count": 32},
            {"ts": current_timestamp + 2, "count": 32}
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
def test_post_device_data_old_timestamps():
    """
    Test POST /devices with timestamps before 1735707600 (January 1, 2025).
    Old timestamps should be silently ignored and the request should succeed.
    """
    url = f"{BASE_URL}/devices"
    headers = get_api_key_headers()
    
    current_timestamp = int(time.time())
    device_id = "deviceOldTimestampTest"
    MIN_TIMESTAMP = 1735707600  # January 1, 2025
    
    payload = {
        "trail_id": 1,
        "name": "f1c9645dbc14efddc7d8a322685f26eb3c0b65c6d5aeb89f9a3a98a4f8f5c0d3",
        "battery": 85,
        "data": [
            {"ts": MIN_TIMESTAMP - 1000, "count": 88},
            {"ts": MIN_TIMESTAMP - 1, "count": 88},
            {"ts": current_timestamp, "count": 88},
            {"ts": MIN_TIMESTAMP, "count": 88},
            {"ts": current_timestamp + 1, "count": 88}
        ]
    }

    response = requests.put(url, json=payload, headers=headers)
    
    print(f"Response Status: {response.status_code}")
    print(f"Response Body: {response.json()}")
    
    assert response.status_code == 200
    response_data = response.json()
    assert "message" in response_data
    assert response_data["message"] == "Device data uploaded successfully"