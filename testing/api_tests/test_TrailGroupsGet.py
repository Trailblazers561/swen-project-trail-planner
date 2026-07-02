import requests
import pytest
from api_config import BASE_URL, get_cognito_headers

@pytest.mark.API
def test_get_area_metadata_success():
    """
    Test GET /areas to retrieve all areas.
    """
    url = f"{BASE_URL}/areas"
    headers = get_cognito_headers()
    
    response = requests.get(url, headers=headers)
    
    assert response.status_code == 200
    areas = response.json()
    assert isinstance(areas, list)
    
    # Verify area structure
    for area in areas:
        assert "name" in area
        assert "trail_ids" in area
        assert isinstance(area["name"], str)
        assert isinstance(area["trail_ids"], list)

@pytest.mark.API
def test_get_area_metadata_structure():
    """
    Test that areas have the correct structure and trail_ids are valid.
    """
    url = f"{BASE_URL}/areas"
    headers = get_cognito_headers()
    
    response = requests.get(url, headers=headers)
    assert response.status_code == 200
    areas = response.json()
    
    # Get all trails to verify trail_ids in areas are valid
    trails_url = f"{BASE_URL}/trail_metadata"
    trails_response = requests.get(trails_url, headers=headers)
    assert trails_response.status_code == 200
    trails = trails_response.json()
    valid_trail_ids = {t["id"] for t in trails}
    
    for area in areas:
        for trail_id in area.get("trail_ids", []):
            assert trail_id in valid_trail_ids, f"Trail ID {trail_id} in area {area['name']} does not exist"

@pytest.mark.API
def test_get_area_metadata_unauthorized():
    """
    Test GET /areas without authentication.
    """
    url = f"{BASE_URL}/areas"
    
    response = requests.get(url)
    
    assert response.status_code in [401, 403]