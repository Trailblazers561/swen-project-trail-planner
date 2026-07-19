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

def test_exception_returns_500(monkeypatch):
    module = load_module()

    def raise_error(*args, **kwargs):
        raise RuntimeError("boom")

    monkeypatch.setattr(module.device_table, "get_item", raise_error)

    event = {
    "body": json.dumps({
        "device_id": 1,
        "is_archived": True
    })
    }

    response = module.set_device_archived(event, None)

    assert response["statusCode"] == 500

