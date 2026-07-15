import importlib
import json

def load_module():
    """
    Import (or reload) the Lambda after Moto has created the mocked AWS
    resources. This ensures the module's global DynamoDB objects point at
    Moto instead of real AWS.
    """
    # DO NOT IMPORT THE FUNCTION UP TOP, IMPORT IT IN THIS FUNCTION
    module = importlib.import_module("lambdas.public_api.trail_metadata.trail_metadata_post")
    return importlib.reload(module)


def test_empty_name_returns_400():
    # Arrange
    module = load_module()
    event = {
        "body": json.dumps({
            "name": ""
        })
    }
    context = {}

    # Act
    response = module.create_trail(event, context)

    # Assert
    assert response["statusCode"] == 400
    assert json.loads(response["body"]) == {"error": "Missing required field: name"}

def test_create_successful_trail():
    # Arrange
    module = load_module()
    event = {
        "body": json.dumps({
            "name": "Test Trail",
            "area_name": "Test Area",
            "notes": "This is a test trail.",
            "latitude": 45.123,
            "longitude": -122.456,
            "date_activated": "2024-06-01T12:00:00"
        })
    }
    context = {}

    # Act
    response = module.create_trail(event, context)

    # Assert
    assert response["statusCode"] == 200
    body = json.loads(response["body"])
    assert "trail_id" in body
    assert body["message"] == "Trail created successfully"

def test_create_trail_to_existing_area():
    # Arrange
    module = load_module()
    event = {
        "body": json.dumps({
            "name": "Test Trail",
            "area_name": "High Peaks Wilderness",
            "notes": "This is a test trail being added to an existing area",
            "latitude": 45,
            "longitude": -122,
            "date_activated": "2024-06-01T12:00:00"
        })
    }
    context = {}

    # Act
    response = module.create_trail(event, context)

    # Assert
    assert response["statusCode"] == 200
    body = json.loads(response["body"])
    assert "trail_id" in body
    assert body["message"] == "Trail created successfully"

def test_empty_date_uses_current_time_when_creating_trail():
    # Arrange
    module = load_module()
    event = {
        "body": json.dumps({
            "name": "Test Trail Without Date",
            "area_name": "Test Area",
            "notes": "This is a test trail.",
            "latitude": 45.123,
            "longitude": -122.456
        })
    }
    context = {}

    # Act
    response = module.create_trail(event, context)

    # Assert
    assert response["statusCode"] == 200
    body = json.loads(response["body"])
    assert "trail_id" in body
    assert body["message"] == "Trail created successfully"

def test_create_with_required_fields_only():
    module = load_module()

    event = {
        "body": json.dumps({
            "name": "Trail with Name only"
        })
    }

    response = module.create_trail(event, None)

    assert response["statusCode"] == 200

    body = json.loads(response["body"])

    assert body["message"] == "Trail created successfully"
    assert isinstance(body["trail_id"], int)

def test_invalid_date_when_creating_trail():
    module = load_module()

    event = {
        "body": json.dumps({
            "name": "Trail",
            "date_activated": "not-a-date"
        })
    }

    response = module.create_trail(event, None)

    assert response["statusCode"] == 500