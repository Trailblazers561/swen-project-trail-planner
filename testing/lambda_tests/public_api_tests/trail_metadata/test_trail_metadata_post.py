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
    assert body["message"] == f"Trail created successfully with ID {body['trail_id']}"

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
    assert body["message"] == f"Trail created successfully with ID {body['trail_id']}"


#auto generated, might not work
def test_create_trail_returns_500():
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

    # Mock the put_item method to raise an exception
    original_put_item = module.trail_table.put_item
    def mock_put_item(Item):
        raise Exception("Simulated DynamoDB failure")
    module.trail_table.put_item = mock_put_item

    # Act
    response = module.create_trail(event, context)

    # Restore the original put_item method
    module.trail_table.put_item = original_put_item

    # Assert
    assert response["statusCode"] == 500
    assert json.loads(response["body"]) == {"error": "Failed to create trail: Simulated DynamoDB failure"}