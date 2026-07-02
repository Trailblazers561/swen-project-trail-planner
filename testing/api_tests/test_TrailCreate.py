import requests
import pytest
import time
from api_config import BASE_URL, get_cognito_headers

@pytest.mark.API
def test_create_trail_success():
    """
    Test POST /trail_metadata to create a new trail.
    """
    url = f"{BASE_URL}/trail_metadata"
    headers = get_cognito_headers()
    
    # Create a unique trail name using timestamp
    trail_name = f"Test Trail {int(time.time())}"
    
    payload = {
        "name": trail_name
    }
    
    response = requests.post(url, json=payload, headers=headers)
    
    assert response.status_code == 200
    data = response.json()
    assert "trail_id" in data
    assert data["trail_id"] > 0
    assert "message" in data
    assert "created" in data["message"].lower() or "success" in data["message"].lower()
    
    # Verify the trail was created by getting all trails
    get_response = requests.get(url, headers=headers)
    assert get_response.status_code == 200
    trails = get_response.json()
    created_trail = next((t for t in trails if t.get("name") == trail_name), None)
    assert created_trail is not None
    assert created_trail["id"] == data["trail_id"]

@pytest.mark.API
def test_create_trail_with_area():
    """
    Test POST /trail_metadata to create a trail with a area.
    """
    url = f"{BASE_URL}/trail_metadata"
    headers = get_cognito_headers()
    
    trail_name = f"Test Area Trail {int(time.time())}"
    area_name = "Test Area"
    
    payload = {
        "name": trail_name,
        "area_name": area_name
    }
    
    response = requests.post(url, json=payload, headers=headers)
    
    assert response.status_code == 200
    data = response.json()
    assert "trail_id" in data
    
    # Verify the trail was added to the area
    areas_url = f"{BASE_URL}/areas"
    areas_response = requests.get(areas_url, headers=headers)
    assert areas_response.status_code == 200
    areas = areas_response.json()
    test_area = next((a for a in areas if a.get("name") == area_name), None)
    assert test_area is not None
    assert data["trail_id"] in test_area.get("trail_ids", [])

@pytest.mark.API
def test_create_trail_missing_name():
    """
    Test POST /trail_metadata with missing trail_name.
    """
    url = f"{BASE_URL}/trail_metadata"
    headers = get_cognito_headers()
    
    payload = {}
    
    response = requests.post(url, json=payload, headers=headers)
    
    assert response.status_code == 400

@pytest.mark.API
def test_create_trail_empty_name():
    """
    Test POST /trail_metadata with empty trail_name.
    """
    url = f"{BASE_URL}/trail_metadata"
    headers = get_cognito_headers()
    
    payload = {
        "name": ""
    }
    
    response = requests.post(url, json=payload, headers=headers)
    
    assert response.status_code in [400, 500]

@pytest.mark.API
def test_create_trail_unauthorized():
    """
    Test POST /trail_metadata without authentication.
    """
    url = f"{BASE_URL}/trail_metadata"
    
    payload = {
        "name": "Unauthorized Trail"
    }
    
    response = requests.post(url, json=payload)
    
    assert response.status_code in [401, 403]