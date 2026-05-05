import requests
import pytest
import time
from api_config import BASE_URL, get_cognito_headers

@pytest.mark.API
def test_update_trail_metadata_success():
    """
    Test PUT /trail_metadata to update trail name and area.
    """
    url = f"{BASE_URL}/trail_metadata"
    headers = get_cognito_headers()
    
    # First, get existing trails to find one to update
    get_url = f"{BASE_URL}/trail_metadata"
    get_response = requests.get(get_url, headers=headers)
    
    assert get_response.status_code == 200
    trails = get_response.json()
    assert len(trails) > 0, "No trails found to update"
    
    # Use the first trail for testing
    test_trail = trails[0]
    trail_id = test_trail.get("id")
    original_name = test_trail.get("name", "")
    
    # Update trail with new name
    new_name = f"{original_name}_updated_{int(time.time())}"
    payload = {
        "trail_id": trail_id,
        "name": new_name
    }
    
    response = requests.put(url, json=payload, headers=headers)
    
    print(f"Response Status: {response.status_code}")
    print(f"Response Body: {response.json()}")
    
    assert response.status_code == 200
    response_data = response.json()
    assert "message" in response_data
    assert "updated successfully" in response_data["message"].lower()
    
    # Verify the update by getting the trail again
    get_response_2 = requests.get(get_url, headers=headers)
    assert get_response_2.status_code == 200
    updated_trails = get_response_2.json()
    updated_trail = next((t for t in updated_trails if t.get("id") == trail_id), None)
    assert updated_trail is not None
    assert updated_trail.get("name") == new_name
    
    # Cleanup: restore original name
    restore_payload = {
        "trail_id": trail_id,
        "name": original_name
    }
    requests.put(url, json=restore_payload, headers=headers)


@pytest.mark.API
def test_update_trail_metadata_with_area():
    """
    Test PUT /trail_metadata to update area.
    """
    url = f"{BASE_URL}/trail_metadata"
    headers = get_cognito_headers()
    
    # Get existing trails and areas
    trails_response = requests.get(f"{BASE_URL}/trail_metadata", headers=headers)
    areas_response = requests.get(f"{BASE_URL}/areas", headers=headers)
    
    assert trails_response.status_code == 200
    assert areas_response.status_code == 200
    
    trails = trails_response.json()
    areas = areas_response.json()
    
    assert len(trails) > 0, "No trails found"
    assert len(areas) > 0, "No areas found"
    
    # Use first trail and first area
    test_trail = trails[0]
    trail_id = test_trail.get("id")
    test_area = areas[0]
    area_name = test_area.get("name")
    
    # Update trail with area
    payload = {
        "trail_id": trail_id,
        "area_name": area_name
    }
    
    response = requests.put(url, json=payload, headers=headers)
    
    print(f"Response Status: {response.status_code}")
    print(f"Response Body: {response.json()}")
    
    assert response.status_code == 200
    response_data = response.json()
    assert "message" in response_data
    
    # Verify the trail is in the area
    areas_response_2 = requests.get(f"{BASE_URL}/areas", headers=headers)
    assert areas_response_2.status_code == 200
    updated_areas = areas_response_2.json()
    updated_area = next((a for a in updated_areas if a.get("name") == area_name), None)
    assert updated_area is not None
    assert trail_id in updated_area.get("trail_ids", [])


@pytest.mark.API
def test_update_trail_metadata_missing_trail_id():
    """
    Test PUT /trail_metadata with missing trail_id - should return 400.
    """
    url = f"{BASE_URL}/trail_metadata"
    headers = get_cognito_headers()
    
    payload = {
        "name": "Test Trail"
    }
    
    response = requests.put(url, json=payload, headers=headers)
    
    print(f"Response Status: {response.status_code}")
    print(f"Response Body: {response.json()}")
    
    assert response.status_code == 400
    response_data = response.json()
    assert "error" in response_data
    assert "trail_id" in response_data["error"].lower()


@pytest.mark.API
def test_update_trail_metadata_invalid_trail_id():
    """
    Test PUT /trail_metadata with invalid trail_id format - should return 400.
    """
    url = f"{BASE_URL}/trail_metadata"
    headers = get_cognito_headers()
    
    payload = {
        "trail_id": "not-a-number",
        "name": "Test Trail"
    }
    
    response = requests.put(url, json=payload, headers=headers)
    
    print(f"Response Status: {response.status_code}")
    print(f"Response Body: {response.json()}")
    
    assert response.status_code == 400
    response_data = response.json()
    assert "error" in response_data


@pytest.mark.API
def test_update_trail_metadata_unauthorized():
    """
    Test PUT /trail_metadata without authentication - should return 401/403.
    """
    url = f"{BASE_URL}/trail_metadata"
    headers = {
        "Content-Type": "application/json"
        # Missing Authorization header
    }
    
    payload = {
        "trail_id": 1,
        "name": "Test Trail"
    }
    
    response = requests.put(url, json=payload, headers=headers)
    
    print(f"Response Status: {response.status_code}")
    
    assert response.status_code in [401, 403]