import requests
import pytest
from api_config import BASE_URL, get_cognito_headers

@pytest.mark.API
def test_get_trail_group_metadata_success():
    """
    Test GET /trail_groups to retrieve all trail groups.
    """
    url = f"{BASE_URL}/trail_groups"
    headers = get_cognito_headers()
    
    response = requests.get(url, headers=headers)
    
    assert response.status_code == 200
    groups = response.json()
    assert isinstance(groups, list)
    
    # Verify group structure
    for group in groups:
        assert "name" in group
        assert "trail_ids" in group
        assert isinstance(group["name"], str)
        assert isinstance(group["trail_ids"], list)

@pytest.mark.API
def test_get_trail_group_metadata_structure():
    """
    Test that trail groups have the correct structure and trail_ids are valid.
    """
    url = f"{BASE_URL}/trail_groups"
    headers = get_cognito_headers()
    
    response = requests.get(url, headers=headers)
    assert response.status_code == 200
    groups = response.json()
    
    # Get all trails to verify trail_ids in groups are valid
    trails_url = f"{BASE_URL}/trail_metadata"
    trails_response = requests.get(trails_url, headers=headers)
    assert trails_response.status_code == 200
    trails = trails_response.json()
    valid_trail_ids = {t["id"] for t in trails}
    
    for group in groups:
        for trail_id in group.get("trail_ids", []):
            assert trail_id in valid_trail_ids, f"Trail ID {trail_id} in group {group['name']} does not exist"

@pytest.mark.API
def test_get_trail_group_metadata_unauthorized():
    """
    Test GET /trail_groups without authentication.
    """
    url = f"{BASE_URL}/trail_groups"
    
    response = requests.get(url)
    
    assert response.status_code in [401, 403]