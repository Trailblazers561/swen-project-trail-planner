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
        assert "id" in device
        assert isinstance(device["id"], int)

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
        assert "id" in device
        # name, notes, firmware_version, date_manufactured, and date_retired are optional
        if "name" in device:
            assert isinstance(device["name"], str)
        if "notes" in device:
            assert isinstance(device["notes"], str)
        if "firmware_version" in device:
            assert isinstance(device["firmware_version"], str)
        if "date_manufactured" in device:
            assert isinstance(device["date_manufactured"], (int, type(None)))
        if "date_retired" in device:
            assert isinstance(device["date_retired"], (int, type(None)))

@pytest.mark.API
def test_get_device_metadata_unauthorized():
    """
    Test GET /device_metadata without authentication.
    """
    url = f"{BASE_URL}/device_metadata"
    
    response = requests.get(url)
    
    assert response.status_code in [401, 403]