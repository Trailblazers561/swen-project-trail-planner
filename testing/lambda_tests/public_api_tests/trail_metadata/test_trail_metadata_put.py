import importlib
import json

def load_module():
    """
    Import (or reload) the Lambda after Moto has created the mocked AWS
    resources. This ensures the module's global DynamoDB objects point at
    Moto instead of real AWS.
    """
    # DO NOT IMPORT THE FUNCTION UP TOP, IMPORT IT IN THIS FUNCTION
    module = importlib.import_module("lambdas.public_api.trail_metadata.trail_metadata_put")
    return importlib.reload(module)

def test_update_name_success():
    module = load_module()

    event = {
        "body": {
            "trail_id": 1,
            "name": "Updated Trail"
        }
    }

    response = module.update_trail_metadata(event, None)

    assert response["statusCode"] == 200

    body = json.loads(response["body"])
    assert body["message"] == "Trail metadata updated successfully"

def test_update_all_fields_success():
    module = load_module()

    event = {
        "body": {
            "trail_id": 1,
            "name": "New Name",
            "area_name": "New Area",
            "notes": "Updated notes",
            "latitude": 43.12,
            "longitude": -77.45
        }
    }

    response = module.update_trail_metadata(event, None)

    assert response["statusCode"] == 200

    body = json.loads(response["body"])
    assert body["message"] == "Trail metadata updated successfully"

def test_empty_body():
    # Arrange
    module = load_module()
    event = {
        "body": json.dumps({})
    }
    context = {}

    # Act
    response = module.update_trail_metadata(event, context)

    # Assert
    assert response["statusCode"] == 400

def test_empty_trail_id():
    # Arrange
    module = load_module()
    event = {
        "body": json.dumps({
            "trail_id": None,
            "name": "Test Trail",
            "area_name": "Test Area",
            "notes": "This is a test trail.",
            "latitude": 45.123,
            "longitude": -122.456,
        })
    }
    context = {}

    # Act
    response = module.update_trail_metadata(event, context)

    # Assert
    assert response["statusCode"] == 400
    body = json.loads(response["body"])
    assert body["error"] == "Missing required field: trail_id"

def test_invalid_trail_id():
    # Arrange
    module = load_module()
    event = {
        "body": json.dumps({
            "trail_id": "test",
            "name": "Test Trail",
            "area_name": "Test Area",
            "notes": "This is a test trail.",
            "latitude": 45.123,
            "longitude": -122.456,
        })
    }
    context = {}

    # Act
    response = module.update_trail_metadata(event, context)

    # Assert
    assert response["statusCode"] == 400
    body = json.loads(response["body"])
    assert body["error"] == "Invalid trail_id format"

def test_invalid_name():
    module = load_module()

    event = {
        "body": {
            "trail_id": 1,
            "name": 123
        }
    }

    response = module.update_trail_metadata(event, None)

    assert response["statusCode"] == 400

    body = json.loads(response["body"])
    assert body["error"] == "Invalid name format"


def test_invalid_area_name():
    module = load_module()

    event = {
        "body": {
            "trail_id": 1,
            "area_name": 123
        }
    }

    response = module.update_trail_metadata(event, None)

    assert response["statusCode"] == 400

    body = json.loads(response["body"])
    assert body["error"] == "Invalid area_name format"


def test_invalid_notes():
    module = load_module()

    event = {
        "body": {
            "trail_id": 1,
            "notes": 123
        }
    }

    response = module.update_trail_metadata(event, None)

    assert response["statusCode"] == 400

    body = json.loads(response["body"])
    assert body["error"] == "Invalid notes format"


def test_invalid_latitude():
    module = load_module()

    event = {
        "body": {
            "trail_id": 1,
            "latitude": "north"
        }
    }

    response = module.update_trail_metadata(event, None)

    assert response["statusCode"] == 400

    body = json.loads(response["body"])
    assert body["error"] == "Invalid latitude format"


def test_invalid_longitude():
    module = load_module()

    event = {
        "body": {
            "trail_id": 1,
            "longitude": "west"
        }
    }

    response = module.update_trail_metadata(event, None)

    assert response["statusCode"] == 400

    body = json.loads(response["body"])
    assert body["error"] == "Invalid longitude format"