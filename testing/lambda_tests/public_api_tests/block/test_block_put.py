import importlib
import json


def load_module():
    """
    Import (or reload) the Lambda after Moto has created the mocked AWS
    resources. This ensures the module's global DynamoDB objects point at
    Moto instead of real AWS.
    """
    module = importlib.import_module(
        "lambdas.public_api.block.block_put"
    )
    return importlib.reload(module)


def test_block_device():
    # Arrange
    module = load_module()

    module.device_table.put_item(
        Item={
            "id": 1,
            "name": "Test Device",
            "is_blocked": False,
        }
    )

    module.device_trail_table.put_item(
        Item={
            "device_id": 1,
            "date_installed": 100,
        }
    )

    event = {
        "body": json.dumps({
            "device_id": 1,
            "is_blocked": True,
        })
    }

    # Act
    response = module.set_device_blocked(event, None)

    # Assert
    assert response["statusCode"] == 200

    device = module.device_table.get_item(
        Key={"id": 1}
    )["Item"]

    assert device["is_blocked"] is True

    device_trail = module.device_trail_table.get_item(
        Key={
            "device_id": 1,
            "date_installed": 100,
        }
    )["Item"]

    assert device_trail["date_removed"] is not None


def test_unblock_device():
    # Arrange
    module = load_module()

    module.device_table.put_item(
        Item={
            "id": 1,
            "name": "Test Device",
            "is_blocked": True,
        }
    )

    module.device_trail_table.put_item(
        Item={
            "device_id": 1,
            "date_installed": 100,
            "date_removed": 12345,
        }
    )

    event = {
        "body": json.dumps({
            "device_id": 1,
            "is_blocked": False,
        })
    }

    # Act
    response = module.set_device_blocked(event, None)

    # Assert
    assert response["statusCode"] == 200

    device = module.device_table.get_item(
        Key={"id": 1}
    )["Item"]

    assert device["is_blocked"] is False

    device_trail = module.device_trail_table.get_item(
        Key={
            "device_id": 1,
            "date_installed": 100,
        }
    )["Item"]

    assert device_trail["date_removed"] == 12345


def test_block_device_updates_multiple_trails():
    # Arrange
    module = load_module()

    module.device_table.put_item(
        Item={
            "id": 1,
            "is_blocked": False,
        }
    )

    module.device_trail_table.put_item(
        Item={
            "device_id": 1,
            "date_installed": 100,
        }
    )

    module.device_trail_table.put_item(
        Item={
            "device_id": 1,
            "date_installed": 200,
        }
    )

    event = {
        "body": json.dumps({
            "device_id": 1,
            "is_blocked": True,
        })
    }

    # Act
    response = module.set_device_blocked(event, None)

    # Assert
    assert response["statusCode"] == 200

    first = module.device_trail_table.get_item(
        Key={
            "device_id": 1,
            "date_installed": 100,
        }
    )["Item"]

    second = module.device_trail_table.get_item(
        Key={
            "device_id": 1,
            "date_installed": 200,
        }
    )["Item"]

    assert first["date_removed"] is not None
    assert second["date_removed"] is not None


def test_block_device_preserves_existing_date_removed():
    # Arrange
    module = load_module()

    module.device_table.put_item(
        Item={
            "id": 1,
            "is_blocked": False,
        }
    )

    module.device_trail_table.put_item(
        Item={
            "device_id": 1,
            "date_installed": 100,
            "date_removed": 9999,
        }
    )

    event = {
        "body": json.dumps({
            "device_id": 1,
            "is_blocked": True,
        })
    }

    # Act
    response = module.set_device_blocked(event, None)

    # Assert
    assert response["statusCode"] == 200

    device_trail = module.device_trail_table.get_item(
        Key={
            "device_id": 1,
            "date_installed": 100,
        }
    )["Item"]

    assert device_trail["date_removed"] == 9999


def test_missing_device_id_returns_400():
    # Arrange
    module = load_module()

    event = {
        "body": json.dumps({
            "is_blocked": True,
        })
    }

    # Act
    response = module.set_device_blocked(event, None)

    # Assert
    assert response["statusCode"] == 400

    body = json.loads(response["body"])

    assert body["error"] == "Missing required field: device_id"


def test_missing_is_blocked_returns_400():
    # Arrange
    module = load_module()

    event = {
        "body": json.dumps({
            "device_id": 1,
        })
    }

    # Act
    response = module.set_device_blocked(event, None)

    # Assert
    assert response["statusCode"] == 400

    body = json.loads(response["body"])

    assert body["error"] == "Missing required field: is_blocked"


def test_unknown_device_returns_404():
    # Arrange
    module = load_module()

    event = {
        "body": json.dumps({
            "device_id": 999,
            "is_blocked": True,
        })
    }

    # Act
    response = module.set_device_blocked(event, None)

    # Assert
    assert response["statusCode"] == 404

    body = json.loads(response["body"])

    assert body["error"] == "Device id not present in table"


def test_invalid_json_returns_400():
    # Arrange
    module = load_module()

    event = {
        "body": "{not valid json"
    }

    # Act
    response = module.set_device_blocked(event, None)

    # Assert
    assert response["statusCode"] == 400

    body = json.loads(response["body"])

    assert body["error"]


def test_invalid_is_blocked_type_returns_400():
    """
    Regression test for bug:
    is_blocked accepted arbitrary values because truthiness
    was used instead of validating bool type.
    """

    # Arrange
    module = load_module()

    module.device_table.put_item(
        Item={
            "id": 1,
            "is_blocked": False,
        }
    )

    event = {
        "body": json.dumps({
            "device_id": 1,
            "is_blocked": "banana",
        })
    }

    # Act
    response = module.set_device_blocked(event, None)

    # Assert
    assert response["statusCode"] == 400

    body = json.loads(response["body"])

    assert body["error"] == "is_blocked must be a boolean"