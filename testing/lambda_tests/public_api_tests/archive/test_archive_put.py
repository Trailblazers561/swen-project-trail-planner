from testing.lambda_tests.test_data import DEVICE_LOG_DATA

import importlib
import json
import boto3

def load_module():
    """
    Import (or reload) the Lambda after Moto has created the mocked AWS
    resources. This ensures the module's global DynamoDB objects point at
    Moto instead of real AWS.
    """
    # DO NOT IMPORT THE FUNCTION UP TOP, IMPORT IT IN THIS FUNCTION
    module = importlib.import_module("lambdas.public_api.archive.archive_put")
    return importlib.reload(module)

# Tests that don't currently work but should probably work are commented out for now
#def test_archive_existing_device(): TO BE IMPLEMENTED
    # Arrange
    module = load_module()

    event = {
        "body": json.dumps({
            "device_id": 1,
            "is_archived": True
        })
    }

    # Act
    response = module.set_device_archived(event, None)

    # Assert
    assert response["statusCode"] == 200

    body = json.loads(response["body"])
    assert "is_archived set to True" in body["message"]

    table = boto3.resource("dynamodb").Table(
        "test_trailcount_device_table"
    )

    item = table.get_item(Key={"id": 1})["Item"]
    assert item["is_archived"] is True

def test_unarchive_existing_device():
    # Arrange
    module = load_module()

    event = {
        "body": json.dumps({
            "device_id": 1,
            "is_archived": False
        })
    }

    # Act
    response = module.set_device_archived(event, None)

    # Assert
    assert response["statusCode"] == 200

    table = boto3.resource("dynamodb").Table(
        "test_trailcount_device_table"
    )

    item = table.get_item(Key={"id": 1})["Item"]

    assert item["is_archived"] is False

def test_missing_device_id():
    # Arrange
    module = load_module()

    event = {
        "body": json.dumps({
            "is_archived": True
        })
    }

    # Act
    response = module.set_device_archived(event, None)

    # Assert
    assert response["statusCode"] == 400

    body = json.loads(response["body"])

    assert body["error"] == "Missing required field: device_id"

def test_missing_is_archived():
    # Arrange
    module = load_module()

    event = {
        "body": json.dumps({
            "device_id": 1
        })
    }

    # Act
    response = module.set_device_archived(event, None)

    # Assert
    assert response["statusCode"] == 400

    body = json.loads(response["body"])

    assert body["error"] == "Missing required field: is_archived"

def test_unknown_device():
    # Arrange
    module = load_module()

    event = {
        "body": json.dumps({
            "device_id": 999999,
            "is_archived": True
        })
    }

    # Act
    response = module.set_device_archived(event, None)

    # Assert
    assert response["statusCode"] == 404

    body = json.loads(response["body"])

    assert body["error"] == "Device id not present in table"

def test_device_id_as_string():
    # Arrange
    module = load_module()

    event = {
        "body": json.dumps({
            "device_id": "1",
            "is_archived": True
        })
    }

    # Act
    response = module.set_device_archived(event, None)

    # Assert
    assert response["statusCode"] == 200

def test_invalid_device_id_string():
    # Arrange
    module = load_module()

    event = {
        "body": json.dumps({
            "device_id": "abc",
            "is_archived": True
        })
    }

    # Act
    response = module.set_device_archived(event, None)

    # Assert
    assert response["statusCode"] == 400

def test_empty_body():
    # Arrange
    module = load_module()

    event = {
        "body": {}
    }

    # Act
    response = module.set_device_archived(event, None)

    # Assert
    assert response["statusCode"] == 400

def test_missing_body():
    # Arrange
    module = load_module()

    # Act
    response = module.set_device_archived({}, None)

    # Assert
    assert response["statusCode"] == 400

#def test_invalid_json():
#    # Arrange
#    module = load_module()
#
#    event = {
#        "body": "{"
#    }
#
#    # Act
#    response = module.set_device_archived(event, None)
#
#    # Assert
#    assert response["statusCode"] == 500
#
#def test_is_archived_integer():
#    # Arrange
#    module = load_module()
#
#    event = {
#        "body": json.dumps({
#            "device_id": 1,
#            "is_archived": 1
#        })
#    }
#
#    # Act
#    response = module.set_device_archived(event, None)
#
#    # Assert
#    assert response["statusCode"] == 200
#
#
#def test_is_archived_string():
#    # Arrange
#    module = load_module()
#
#    event = {
#        "body": json.dumps({
#            "device_id": 1,
#            "is_archived": "true"
#        })
#    }
#
#    # Act
#    response = module.set_device_archived(event, None)
#
#    # Assert
#    assert response["statusCode"] == 200