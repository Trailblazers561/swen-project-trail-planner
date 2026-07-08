import importlib
import json

def load_module():
    """
    Import (or reload) the Lambda after Moto has created the mocked AWS
    resources. This ensures the module's global DynamoDB objects point at
    Moto instead of real AWS.
    """
    # DO NOT IMPORT THE FUNCTION UP TOP, IMPORT IT IN THIS FUNCTION
    module = importlib.import_module("lambdas.public_api.trail_data.trail_data_post")
    return importlib.reload(module)


def test_error_for_invalid_timestamp():
    #Arrange
    module = load_module()

    event = {
        "body": {
            "trail_id": 1,
            "data": [
                {
                    "timestamp": "fake_timestamp",
                    "device_id": 1,
                    "count": 10,
                    "battery": 95
                }
            ]
        }
    }

    #Act
    response = module.upload_trail_data(event, None)

    #Assert
    assert response["statusCode"] == 400

    body = json.loads(response["body"])
    assert body["error"] == "Invalid timestamp format (data[0])"

def test_error_for_no_trail_id():
    #Arrange
    module = load_module()

    event = {
        "body": {
            "data": [
                {
                    "timestamp": 1767225600,
                    "device_id": 1,
                    "count": 10,
                    "battery": 95
                }
            ]
        }
    }

    #Act
    response = module.upload_trail_data(event, None)

    #Assert
    assert response["statusCode"] == 400

    body = json.loads(response["body"])
    assert body["error"] == "Missing required field: trail_id"


def test_error_for_empty_data():
    #Arrange
    module = load_module()

    event = {
        "body": {
            "data": []
        }
    }

    #Act
    response = module.upload_trail_data(event, None)

    #Assert
    assert response["statusCode"] == 400

def test_error_for_no_timestamp():
    #Arrange
    module = load_module()

    event = {
        "body": {
            "trail_id": 1,
            "data": [
                {
                    "count": 10,
                    "device_id": 1,
                    "battery": 95
                }
            ]
        }
    }

    #Act
    response = module.upload_trail_data(event, None)

    #Assert
    assert response["statusCode"] == 400

def test_error_for_no_device_id():
    #Arrange
    module = load_module()

    event = {
        "body": {
            "trail_id": 1,
            "data": [
                {
                    "timestamp": 1767225600,
                    "count": 10,
                    "battery": 95
                }
            ]
        }
    }

    #Act
    response = module.upload_trail_data(event, None)

    #Assert
    assert response["statusCode"] == 400

def test_error_for_no_count():
    #Arrange
    module = load_module()

    event = {
        "body": {
            "trail_id": 1,
            "data": [
                {
                    "timestamp": 1767225600,
                    "device_id": 1,
                    "battery": 95
                }
            ]
        }
    }

    #Act
    response = module.upload_trail_data(event, None)

    #Assert
    assert response["statusCode"] == 400

def test_error_for_no_battery():
    #Arrange
    module = load_module()

    event = {
        "body": {
            "trail_id": 1,
            "data": [
                {
                    "timestamp": 1767225600,
                    "device_id": 1,
                    "count": 10
                }
            ]
        }
    }

    #Act
    response = module.upload_trail_data(event, None)

    #Assert
    assert response["statusCode"] == 400

def test_single_data_point_upload():
    #Arrange
    module = load_module()

    event = {
        "body": {
            "trail_id": 1,
            "data": [
                {
                    "timestamp": 1767225600,
                    "device_id": 1,
                    "count": 10,
                    "battery": 95
                }
            ]
        }
    }

    #Act
    response = module.upload_trail_data(event, None)

    #Assert
    assert response["statusCode"] == 200

    body = json.loads(response["body"])
    assert body["message"] == "Trail data uploaded"

def test_multiple_data_points_upload():
    # Arrange
    module = load_module()

    event = {
        "body": {
            "trail_id": 1,
            "data": [
                {
                    "timestamp": 1767225600,
                    "device_id": 1,
                    "count": 10,
                    "battery": 95
                },
                {
                    "timestamp": 1767229200, #one hour later
                    "device_id": 1,
                    "count": 12,
                    "battery": 94
                },
                {
                    "timestamp": 1767232800, #another hour later
                    "device_id": 1,
                    "count": 15,
                    "battery": 93
                }
            ]
        }
    }

    # Act
    response = module.upload_trail_data(event, None)

    # Assert
    assert response["statusCode"] == 200

    body = json.loads(response["body"])
    assert body["message"] == "Trail data uploaded"


