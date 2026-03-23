import requests
import pytest
from api_config import BASE_URL, get_cognito_headers

@pytest.mark.API
def test_get_device_metadata_success():
    """
    Test GET /device_metadata to retrieve all device metadata.
    """
    url = f"{BASE_URL}/device_metadata"
    headers = get_cognito_headers()
    
    response = requests.get(url, headers=headers)
    
    assert response.status_code == 200
    devices = response.json()
    assert isinstance(devices, list)
    
    # Verify device structure if devices exist
    for device in devices:
        assert "device_id" in device
        assert isinstance(device["device_id"], str)

@pytest.mark.API
def test_get_device_metadata_structure():
    """
    Test that device metadata has the correct structure.
    """
    url = f"{BASE_URL}/device_metadata"
    headers = get_cognito_headers()
    
    response = requests.get(url, headers=headers)
    assert response.status_code == 200
    devices = response.json()
    
    # If devices exist, verify they have expected fields
    if len(devices) > 0:
        device = devices[0]
        assert "device_id" in device
        # trail_id and battery_level are optional
        if "trail_id" in device:
            assert isinstance(device["trail_id"], (int, type(None)))
        if "battery_level" in device:
            assert isinstance(device["battery_level"], (int, float, type(None)))

@pytest.mark.API
def test_get_device_metadata_unauthorized():
    """
    Test GET /device_metadata without authentication.
    """
    url = f"{BASE_URL}/device_metadata"
    
    response = requests.get(url)
    
    assert response.status_code in [401, 403]