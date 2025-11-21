import requests
import pytest
import time
from config import BASE_URL, get_api_key_headers, get_cognito_headers

@pytest.mark.API
def test_device_default_trail_id_from_previous_logs():
    """
    Test that when a device posts data without trail_id, it uses the trail_id
    from the most recent log entry for that device.
    
    Steps:
    1. Post data with trail_id=5 to establish device-trail link
    2. Post data without trail_id (should default to trail_id=5)
    3. Verify the second post's data is associated with trail_id=5
    """
    url = f"{BASE_URL}/devices"
    headers = get_api_key_headers()
    
    device_id = f"deviceDefaultTrailTest_{int(time.time())}"
    base_timestamp = int(time.time())
    
    # Step 1: Post initial data with explicit trail_id=5
    initial_payload = {
        "trail_id": 5,
        "device_id": device_id,
        "battery": 90,
        "data": [
            {"ts": base_timestamp}
        ]
    }
    
    response_1 = requests.post(url, json=initial_payload, headers=headers)
    print(f"Initial POST Response Status: {response_1.status_code}")
    print(f"Initial POST Response Body: {response_1.json()}")
    
    assert response_1.status_code == 200
    response_data_1 = response_1.json()
    assert "message" in response_data_1
    assert response_data_1["message"] == "Device data uploaded successfully"
    
    # Wait to ensure data is written
    time.sleep(1)
    
    # Step 2: Post data WITHOUT trail_id (should default to trail_id=5)
    default_payload = {
        "device_id": device_id,
        "battery": 85,
        "data": [
            {"ts": base_timestamp + 10}
        ]
    }
    
    response_2 = requests.post(url, json=default_payload, headers=headers)
    print(f"Default POST Response Status: {response_2.status_code}")
    print(f"Default POST Response Body: {response_2.json()}")
    
    assert response_2.status_code == 200
    response_data_2 = response_2.json()
    assert "message" in response_data_2
    assert response_data_2["message"] == "Device data uploaded successfully"
    
    # Wait to ensure data is written
    time.sleep(1)
    
    # Step 3: Verify both data points are associated with trail_id=5
    trail_data_url = f"{BASE_URL}/trail_data"
    cognito_headers = get_cognito_headers()
    
    # Query for trail_id=5
    params = {
        "trails": "5"
    }
    
    response_3 = requests.get(trail_data_url, headers=cognito_headers, params=params)
    print(f"GET Trail Data Response Status: {response_3.status_code}")
    
    assert response_3.status_code == 200
    trail_data = response_3.json()
    assert isinstance(trail_data, list)
    
    # Find entries for device
    device_entries = [entry for entry in trail_data if entry.get("device_id") == device_id]
    print(f"Found {len(device_entries)} entries for device {device_id}")
    
    # Verify there are at least 2 entries (initial + default)
    assert len(device_entries) >= 2, f"Expected at least 2 entries, found {len(device_entries)}"
    
    # Verify all entries have trail_id=5
    for entry in device_entries:
        assert entry.get("trail_id") == 5, f"Expected trail_id=5, got {entry.get('trail_id')}"
        assert entry.get("device_id") == device_id
        assert "timestamp" in entry
    
    # Verify specific timestamps are present
    timestamps = [entry.get("timestamp") for entry in device_entries]
    assert base_timestamp in timestamps, "Initial timestamp not found"
    assert (base_timestamp + 10) in timestamps, "Default timestamp not found"
    
    print(f"✓ Successfully verified default trail_id resolution for device {device_id}")


@pytest.mark.API
def test_device_default_trail_id_from_metadata():
    """
    Test that when a device posts data without trail_id, it uses the trail_id
    from DeviceMetadata table if available.
    
    Steps:
    1. Post data with trail_id=7 to create DeviceMetadata entry
    2. Post data without trail_id (should use trail_id=7 from metadata)
    3. Verify the second post's data is associated with trail_id=7
    """
    url = f"{BASE_URL}/devices"
    headers = get_api_key_headers()
    
    device_id = f"deviceMetadataTest_{int(time.time())}"
    base_timestamp = int(time.time())
    
    # Step 1: Post initial data with explicit trail_id=7 to create metadata
    initial_payload = {
        "trail_id": 7,
        "device_id": device_id,
        "battery": 92,
        "data": [
            {"ts": base_timestamp}
        ]
    }
    
    response_1 = requests.post(url, json=initial_payload, headers=headers)
    print(f"Initial POST Response Status: {response_1.status_code}")
    print(f"Initial POST Response Body: {response_1.json()}")
    
    assert response_1.status_code == 200
    
    # Wait to ensure metadata is written
    time.sleep(1)
    
    # Step 2: Post data WITHOUT trail_id (should use trail_id=7 from DeviceMetadata)
    default_payload = {
        "device_id": device_id,
        "battery": 88,
        "data": [
            {"ts": base_timestamp + 20}
        ]
    }
    
    response_2 = requests.post(url, json=default_payload, headers=headers)
    print(f"Default POST Response Status: {response_2.status_code}")
    print(f"Default POST Response Body: {response_2.json()}")
    
    assert response_2.status_code == 200
    response_data_2 = response_2.json()
    assert "message" in response_data_2
    assert response_data_2["message"] == "Device data uploaded successfully"
    
    # Wait to ensure data is written
    time.sleep(1)
    
    # Step 3: Verify both data points are associated with trail_id=7
    trail_data_url = f"{BASE_URL}/trail_data"
    cognito_headers = get_cognito_headers()
    
    # Query for trail_id=7
    params = {
        "trails": "7"
    }
    
    response_3 = requests.get(trail_data_url, headers=cognito_headers, params=params)
    print(f"GET Trail Data Response Status: {response_3.status_code}")
    
    assert response_3.status_code == 200
    trail_data = response_3.json()
    assert isinstance(trail_data, list)
    
    # Find entries for device
    device_entries = [entry for entry in trail_data if entry.get("device_id") == device_id]
    print(f"Found {len(device_entries)} entries for device {device_id}")
    
    # Verify there are at least 2 entries (initial + default)
    assert len(device_entries) >= 2, f"Expected at least 2 entries, found {len(device_entries)}"
    
    # Verify all entries have trail_id=7
    for entry in device_entries:
        assert entry.get("trail_id") == 7, f"Expected trail_id=7, got {entry.get('trail_id')}"
        assert entry.get("device_id") == device_id
        assert "timestamp" in entry
    
    # Verify specific timestamps are present
    timestamps = [entry.get("timestamp") for entry in device_entries]
    assert base_timestamp in timestamps, "Initial timestamp not found"
    assert (base_timestamp + 20) in timestamps, "Default timestamp not found"
    
    print(f"✓ Successfully verified default trail_id resolution from DeviceMetadata for device {device_id}")


@pytest.mark.API
def test_device_default_trail_id_new_device():
    """
    Test that a new device (no previous logs or metadata) defaults to trail_id=0
    when posting data without trail_id.
    
    Steps:
    1. Post data without trail_id for a brand new device
    2. Verify the data is associated with trail_id=0 (default for new devices)
    """
    url = f"{BASE_URL}/devices"
    headers = get_api_key_headers()
    
    device_id = f"deviceNewDeviceTest_{int(time.time())}"
    base_timestamp = int(time.time())
    
    # Post data WITHOUT trail_id for a brand new device
    payload = {
        "device_id": device_id,
        "battery": 95,
        "data": [
            {"ts": base_timestamp}
        ]
    }
    
    response = requests.post(url, json=payload, headers=headers)
    print(f"POST Response Status: {response.status_code}")
    print(f"POST Response Body: {response.json()}")
    
    assert response.status_code == 200
    response_data = response.json()
    assert "message" in response_data
    assert response_data["message"] == "Device data uploaded successfully"
    
    # Wait to ensure data is written
    time.sleep(1)
    
    # Verify the data is associated with trail_id=0 (default for new devices)
    trail_data_url = f"{BASE_URL}/trail_data"
    cognito_headers = get_cognito_headers()
    
    # Query for trail_id=0
    params = {
        "trails": "0"
    }
    
    response_2 = requests.get(trail_data_url, headers=cognito_headers, params=params)
    print(f"GET Trail Data Response Status: {response_2.status_code}")
    
    assert response_2.status_code == 200
    trail_data = response_2.json()
    assert isinstance(trail_data, list)
    
    # Find entry for device
    device_entries = [entry for entry in trail_data if entry.get("device_id") == device_id]
    print(f"Found {len(device_entries)} entries for device {device_id}")
    
    # Verify there are at least 1 entry
    assert len(device_entries) >= 1, f"Expected at least 1 entry, found {len(device_entries)}"
    
    # Verify the entry has trail_id=0
    for entry in device_entries:
        assert entry.get("trail_id") == 0, f"Expected trail_id=0 for new device, got {entry.get('trail_id')}"
        assert entry.get("device_id") == device_id
        assert "timestamp" in entry
    
    print(f"✓ Successfully verified default trail_id=0 for new device {device_id}")

