import requests
import pytest
import time
from api_config import BASE_URL, get_cognito_headers, get_api_key_headers

@pytest.mark.API
@pytest.mark.skip(reason="deprecated")
def test_delete_trail_success():
    """
    Test DELETE /trail_metadata to delete a trail and all associated data.
    """
    url = f"{BASE_URL}/trail_metadata"
    headers = get_cognito_headers()
    
    # First, create a test trail by updating metadata
    # Get existing trails to find a safe one to delete, or create test data
    trails_response = requests.get(url, headers=headers)
    assert trails_response.status_code == 200
    trails = trails_response.json()
    
    # Create a test trail with a unique name
    test_trail_name = f"test_trail_delete_{int(time.time())}"
    test_trail_id = max([t.get("trail_id", 0) for t in trails], default=0) + 1
    
    # Create the trail metadata
    create_payload = {
        "trail_id": test_trail_id,
        "trail_name": test_trail_name
    }
    
    create_response = requests.put(url, json=create_payload, headers=headers)
    assert create_response.status_code == 200
    
    # Create some test device data associated with this trail
    device_id = f"test_device_delete_{int(time.time())}"
    devices_url = f"{BASE_URL}/devices"
    api_headers = get_api_key_headers()
    
    device_payload = {
        "device_id": device_id,
        "trail_id": test_trail_id,
        "battery": 90,
        "data": [
            {"ts": int(time.time())}
        ]
    }
    
    device_response = requests.post(devices_url, json=device_payload, headers=api_headers)
    assert device_response.status_code == 200
    
    # Wait a moment for data to be written
    time.sleep(1)
    
    # Now delete the trail
    delete_payload = {
        "trail_id": test_trail_id
    }
    
    response = requests.delete(url, json=delete_payload, headers=headers)
    
    print(f"Response Status: {response.status_code}")
    print(f"Response Body: {response.json()}")
    
    assert response.status_code == 200
    response_data = response.json()
    assert "message" in response_data
    assert "deleted successfully" in response_data["message"].lower()
    
    # Verify the trail is deleted
    trails_response_2 = requests.get(url, headers=headers)
    assert trails_response_2.status_code == 200
    updated_trails = trails_response_2.json()
    deleted_trail = next((t for t in updated_trails if t.get("trail_id") == test_trail_id), None)
    assert deleted_trail is None, "Trail should be deleted"
    
    # Verify device was reset to trail_id 0
    device_metadata_response = requests.get(f"{BASE_URL}/device_metadata", headers=headers)
    assert device_metadata_response.status_code == 200
    devices = device_metadata_response.json()
    device = next((d for d in devices if d.get("device_id") == device_id), None)
    if device:
        assert device.get("current_trail_id") == 0, "Device should be reset to trail_id 0"


@pytest.mark.API
@pytest.mark.skip(reason="deprecated")
def test_delete_trail_missing_trail_id():
    """
    Test DELETE /trail_metadata with missing trail_id - should return 400.
    """
    url = f"{BASE_URL}/trail_metadata"
    headers = get_cognito_headers()
    
    payload = {}
    
    response = requests.delete(url, json=payload, headers=headers)
    
    print(f"Response Status: {response.status_code}")
    print(f"Response Body: {response.json()}")
    
    assert response.status_code == 400
    response_data = response.json()
    assert "error" in response_data
    assert "trail_id" in response_data["error"].lower()


@pytest.mark.API
@pytest.mark.skip(reason="deprecated")
def test_delete_trail_invalid_trail_id():
    """
    Test DELETE /trail_metadata with invalid trail_id format - should return 400.
    """
    url = f"{BASE_URL}/trail_metadata"
    headers = get_cognito_headers()
    
    payload = {
        "trail_id": "not-a-number"
    }
    
    response = requests.delete(url, json=payload, headers=headers)
    
    print(f"Response Status: {response.status_code}")
    print(f"Response Body: {response.json()}")
    
    assert response.status_code == 400
    response_data = response.json()
    assert "error" in response_data


@pytest.mark.API
@pytest.mark.skip(reason="deprecated")
def test_delete_trail_unauthorized():
    """
    Test DELETE /trail_metadata without authentication - should return 401/403.
    """
    url = f"{BASE_URL}/trail_metadata"
    headers = {
        "Content-Type": "application/json"
        # Missing Authorization header
    }
    
    payload = {
        "trail_id": 1
    }
    
    response = requests.delete(url, json=payload, headers=headers)
    
    print(f"Response Status: {response.status_code}")
    
    assert response.status_code in [401, 403]


@pytest.mark.API
@pytest.mark.skip(reason="deprecated")
def test_delete_trail_removes_from_groups():
    """
    Test that deleting a trail removes it from all trail groups.
    """
    url = f"{BASE_URL}/trail_metadata"
    headers = get_cognito_headers()
    
    # Get existing trails and groups
    trails_response = requests.get(url, headers=headers)
    groups_response = requests.get(f"{BASE_URL}/trail_groups", headers=headers)
    
    assert trails_response.status_code == 200
    assert groups_response.status_code == 200
    
    trails = trails_response.json()
    groups = groups_response.json()
    
    if len(trails) == 0 or len(groups) == 0:
        pytest.skip("Need at least one trail and one group for this test")
    
    # Use first trail and first group
    test_trail = trails[0]
    trail_id = test_trail.get("trail_id")
    test_group = groups[0]
    group_name = test_group.get("group_name")
    
    # Add trail to group first
    update_payload = {
        "trail_id": trail_id,
        "trail_group": group_name
    }
    update_response = requests.put(url, json=update_payload, headers=headers)
    assert update_response.status_code == 200
    
    # Wait a moment
    time.sleep(1)
    
    # Verify trail is in group
    groups_response_2 = requests.get(f"{BASE_URL}/trail_groups", headers=headers)
    assert groups_response_2.status_code == 200
    updated_groups = groups_response_2.json()
    updated_group = next((g for g in updated_groups if g.get("group_name") == group_name), None)
    assert updated_group is not None
    assert trail_id in updated_group.get("trail_ids", [])
    
    # Delete the trail
    delete_payload = {
        "trail_id": trail_id
    }
    delete_response = requests.delete(url, json=delete_payload, headers=headers)
    
    # Note: This test might fail if the trail is the only one in the system
    if delete_response.status_code == 200:
        # Verify trail is removed from group
        groups_response_3 = requests.get(f"{BASE_URL}/trail_groups", headers=headers)
        assert groups_response_3.status_code == 200
        final_groups = groups_response_3.json()
        final_group = next((g for g in final_groups if g.get("group_name") == group_name), None)
        if final_group:
            assert trail_id not in final_group.get("trail_ids", []), "Trail should be removed from group"