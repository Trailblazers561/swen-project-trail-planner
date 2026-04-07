import requests
import pytest
import time
from api_config import BASE_URL, get_cognito_headers, get_api_key_headers

@pytest.mark.API
def test_update_device_trail_association_success():
    """
    Test PUT /device_metadata to associate a device to a trail.
    """
    url = f"{BASE_URL}/device_metadata"
    headers = get_cognito_headers()
    
    # First, create a device with some data to establish it
    devices_url = f"{BASE_URL}/devices"
    api_headers = get_api_key_headers()
    
    # Post device data with trail_id=0
    device_payload = {
        "name": "deviceNameUpdateTrailSuccess",
        "firmware_version": "1.23.15123", 
        "date_manufactured": "2026-03-29"
    }
    
    device_response = requests.post(devices_url, json=device_payload, headers=api_headers)
    assert device_response.status_code == 200
    
    device_id = device_response.json()["device_id"]
    
    # Wait a moment
    time.sleep(1)
    
    # Get available trails
    trails_response = requests.get(f"{BASE_URL}/trail_metadata", headers=headers)
    assert trails_response.status_code == 200
    trails = trails_response.json()
    assert len(trails) > 0, "No trails found"
    
    # Use first trail
    target_trail_id = trails[0].get("id")
    
    # Associate device to trail
    payload = {
        "device_id": device_id,
        "trail_id": target_trail_id
    }
    
    response = requests.put(url, json=payload, headers=headers)
    
    print(f"Response Status: {response.status_code}")
    print(f"Response Body: {response.json()}")
    
    assert response.status_code == 200
    response_data = response.json()
    assert "message" in response_data
    assert "updated successfully" in response_data["message"].lower()
    
    # Verify the association by getting device metadata
    get_response = requests.get(url, headers=headers)
    assert get_response.status_code == 200
    devices = get_response.json()
    device = next((d for d in devices if d.get("id") == device_id), None)
    assert device is not None
    assert device.get("current_trail_id") == target_trail_id


@pytest.mark.API
def test_update_device_trail_association_missing_device_id():
    """
    Test PUT /device_metadata with missing device_id - should return 400.
    """
    url = f"{BASE_URL}/device_metadata"
    headers = get_cognito_headers()
    
    payload = {
        "trail_id": 1
    }
    
    response = requests.put(url, json=payload, headers=headers)
    
    print(f"Response Status: {response.status_code}")
    print(f"Response Body: {response.json()}")
    
    assert response.status_code == 400
    response_data = response.json()
    assert "error" in response_data
    assert "device_id" in response_data["error"].lower()


@pytest.mark.API
def test_update_device_trail_association_missing_trail_id():
    """
    Test PUT /device_metadata with missing trail_id - should return 400.
    """
    url = f"{BASE_URL}/device_metadata"
    headers = get_cognito_headers()
    
    payload = {
        "device_id": 1
    }
    
    response = requests.put(url, json=payload, headers=headers)
    
    print(f"Response Status: {response.status_code}")
    print(f"Response Body: {response.json()}")
    
    assert response.status_code == 400
    response_data = response.json()
    assert "error" in response_data
    assert "trail_id" in response_data["error"].lower()


@pytest.mark.API
def test_update_device_trail_association_invalid_trail_id():
    """
    Test PUT /device_metadata with invalid trail_id format - should return 400.
    """
    url = f"{BASE_URL}/device_metadata"
    headers = get_cognito_headers()
    
    payload = {
        "device_id": "test_device",
        "trail_id": "not-a-number"
    }
    
    response = requests.put(url, json=payload, headers=headers)
    
    print(f"Response Status: {response.status_code}")
    print(f"Response Body: {response.json()}")
    
    assert response.status_code == 400
    response_data = response.json()
    assert "error" in response_data


@pytest.mark.API
def test_update_device_trail_association_unauthorized():
    """
    Test PUT /device_metadata without authentication - should return 401/403.
    """
    url = f"{BASE_URL}/device_metadata"
    headers = {
        "Content-Type": "application/json"
        # Missing Authorization header
    }
    
    payload = {
        "device_id": "test_device",
        "trail_id": 1
    }
    
    response = requests.put(url, json=payload, headers=headers)
    
    print(f"Response Status: {response.status_code}")
    
    assert response.status_code in [401, 403]