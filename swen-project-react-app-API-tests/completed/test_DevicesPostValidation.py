import requests
import pytest
import time
from config import BASE_URL, get_api_key_headers

@pytest.mark.API
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
        "device_id": "deviceF",
        "battery": 94,
        "data": [
            {"ts": current_timestamp}
        ]
    }

    response = requests.post(url, json=payload, headers=headers)
    
    print(f"Response Status: {response.status_code}")
    print(f"Response Body: {response.text}")
    
    assert response.status_code == 403


@pytest.mark.API
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
        "device_id": "deviceG",
        "battery": 94,
        "data": [
            {"ts": current_timestamp}
        ]
    }

    response = requests.post(url, json=payload, headers=headers)
    
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
            {"ts": int(time.time())}
        ]
    }

    response = requests.post(url, json=payload, headers=headers)

    print(f"Response Status: {response.status_code}")
    print(f"Response Body: {response.json()}")

    assert response.status_code == 400
    response_data = response.json()
    assert "error" in response_data
    assert "device_id" in response_data["error"]


@pytest.mark.API
def test_post_device_data_missing_data_array():
    """
    Test POST /devices with missing data array - should return 400 Bad Request.
    """
    url = f"{BASE_URL}/devices"
    headers = get_api_key_headers()

    payload = {
        "trail_id": 1,
        "device_id": "deviceH",
        "battery": 92
    }

    response = requests.post(url, json=payload, headers=headers)

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
        "device_id": "deviceI",
        "data": []
    }

    response = requests.post(url, json=payload, headers=headers)

    print(f"Response Status: {response.status_code}")
    print(f"Response Body: {response.json()}")

    assert response.status_code == 400
    response_data = response.json()
    assert "data array" in response_data["error"].lower()


@pytest.mark.API
def test_post_device_data_missing_timestamp_in_entry():
    """
    Test POST /devices with missing ts in a data entry - should return 400 Bad Request.
    """
    url = f"{BASE_URL}/devices"
    headers = get_api_key_headers()

    payload = {
        "trail_id": 1,
        "device_id": "deviceJ",
        "data": [
            {}
        ]
    }

    response = requests.post(url, json=payload, headers=headers)

    print(f"Response Status: {response.status_code}")
    print(f"Response Body: {response.json()}")

    assert response.status_code == 400
    response_data = response.json()
    assert "ts" in response_data["error"]


@pytest.mark.API
def test_post_device_data_invalid_trail_id_override():
    """
    Test POST /devices with invalid trail_id override - should return 400 Bad Request.
    """
    url = f"{BASE_URL}/devices"
    headers = get_api_key_headers()

    payload = {
        "device_id": "deviceK",
        "trail_id": "not-an-int",
        "data": [
            {"ts": int(time.time())}
        ]
    }

    response = requests.post(url, json=payload, headers=headers)

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
        "device_id": "deviceL",
        "data": [
            {"ts": "not-a-number"}
        ]
    }

    response = requests.post(url, json=payload, headers=headers)

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

    response = requests.post(url, json=payload, headers=headers)
    
    print(f"Response Status: {response.status_code}")
    print(f"Response Body: {response.json()}")
    
    assert response.status_code == 400
    response_data = response.json()
    assert "error" in response_data

