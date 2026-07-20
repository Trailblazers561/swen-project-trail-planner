#import the test data you need
from testing.lambda_tests.test_data import AREA_DATA

import importlib
import json


def load_module():
    """
    Import (or reload) the Lambda after Moto has created the mocked AWS
    resources. This ensures the module's global DynamoDB objects point at
    Moto instead of real AWS.
    """
    module = importlib.import_module("lambdas.public_api.areas.areas_put")
    return importlib.reload(module)


def test_update_area_name():
    # Arrange
    module = load_module()

    original_name = AREA_DATA[0]["name"]

    event = {
        "body": json.dumps({
            "original_name": original_name,
            "new_name": "Renamed Area",
        })
    }

    # Act
    response = module.update_area(event, None)

    # Assert
    assert response["statusCode"] == 200

    body = json.loads(response["body"])
    assert body["message"] == "Area updated successfully"

    old = module.area_table.get_item(Key={"name": original_name}).get("Item")
    new = module.area_table.get_item(Key={"name": "Renamed Area"}).get("Item")

    assert old is None
    assert new is not None
    assert new["name"] == "Renamed Area"


def test_update_area_trails():
    # Arrange
    module = load_module()

    original_name = AREA_DATA[0]["name"]

    event = {
        "body": json.dumps({
            "original_name": original_name,
            "trail_ids": [11, 22, 33],
        })
    }

    # Act
    response = module.update_area(event, None)

    # Assert
    assert response["statusCode"] == 200

    updated = module.area_table.get_item(
        Key={"name": original_name}
    )["Item"]

    assert updated["trail_ids"] == [11, 22, 33]


def test_update_area_name_and_trails():
    # Arrange
    module = load_module()

    original_name = AREA_DATA[0]["name"]

    event = {
        "body": json.dumps({
            "original_name": original_name,
            "new_name": "Updated Area",
            "trail_ids": [5, 6],
        })
    }

    # Act
    response = module.update_area(event, None)

    # Assert
    assert response["statusCode"] == 200

    updated = module.area_table.get_item(
        Key={"name": "Updated Area"}
    )["Item"]

    assert updated["trail_ids"] == [5, 6]


def test_update_area_empty_trails():
    # Arrange
    module = load_module()

    original_name = AREA_DATA[0]["name"]

    event = {
        "body": json.dumps({
            "original_name": original_name,
            "trail_ids": [],
        })
    }

    # Act
    response = module.update_area(event, None)

    # Assert
    assert response["statusCode"] == 200

    updated = module.area_table.get_item(
        Key={"name": original_name}
    )["Item"]

    assert updated["trail_ids"] == []


def test_update_preserves_trails_when_not_provided():
    # Arrange
    module = load_module()

    original_name = AREA_DATA[0]["name"]

    module.area_table.put_item(
        Item={
            "name": original_name,
            "trail_ids": [7, 8, 9],
        }
    )

    event = {
        "body": json.dumps({
            "original_name": original_name,
            "new_name": "Renamed Area",
        })
    }

    # Act
    response = module.update_area(event, None)

    # Assert
    assert response["statusCode"] == 200

    updated = module.area_table.get_item(
        Key={"name": "Renamed Area"}
    )["Item"]

    assert updated["trail_ids"] == [7, 8, 9]


def test_update_reassigns_trails():
    # Arrange
    module = load_module()

    area_a = AREA_DATA[0]["name"]
    area_b = AREA_DATA[1]["name"]

    module.area_table.put_item(
        Item={
            "name": area_a,
            "trail_ids": [1, 2, 3],
        }
    )

    module.area_table.put_item(
        Item={
            "name": area_b,
            "trail_ids": [4],
        }
    )

    event = {
        "body": json.dumps({
            "original_name": area_b,
            "trail_ids": [2, 4],
        })
    }

    # Act
    response = module.update_area(event, None)

    # Assert
    assert response["statusCode"] == 200

    first = module.area_table.get_item(Key={"name": area_a})["Item"]
    second = module.area_table.get_item(Key={"name": area_b})["Item"]

    assert first["trail_ids"] == [1, 3]
    assert second["trail_ids"] == [2, 4]


def test_missing_original_name_returns_400():
    # Arrange
    module = load_module()

    event = {
        "body": json.dumps({
            "new_name": "New Name",
        })
    }

    # Act
    response = module.update_area(event, None)

    # Assert
    assert response["statusCode"] == 400

    body = json.loads(response["body"])

    assert body["error"] == "Missing required field: original_name"


def test_missing_new_name_and_trails_returns_400():
    # Arrange
    module = load_module()

    event = {
        "body": json.dumps({
            "original_name": AREA_DATA[0]["name"],
        })
    }

    # Act
    response = module.update_area(event, None)

    # Assert
    assert response["statusCode"] == 400

    body = json.loads(response["body"])

    assert body["error"] == "Missing required field: new_name or trail_ids"


def test_invalid_trail_ids_returns_400():
    # Arrange
    module = load_module()

    event = {
        "body": json.dumps({
            "original_name": AREA_DATA[0]["name"],
            "trail_ids": ["bad", 2],
        })
    }

    # Act
    response = module.update_area(event, None)

    # Assert
    assert response["statusCode"] == 400

    body = json.loads(response["body"])

    assert body["error"] == "Invalid trail_ids format"


def test_unknown_area_returns_400():
    # Arrange
    module = load_module()

    event = {
        "body": json.dumps({
            "original_name": "Does Not Exist",
            "new_name": "New Name",
        })
    }

    # Act
    response = module.update_area(event, None)

    # Assert
    assert response["statusCode"] == 400

    body = json.loads(response["body"])

    assert "Cannot find area" in body["error"]


def test_invalid_json_returns_400():
    # Arrange
    module = load_module()

    event = {
        "body": "{not valid json"
    }

    # Act
    response = module.update_area(event, None)

    # Assert
    assert response["statusCode"] == 400

    body = json.loads(response["body"])

    assert body["error"]


def test_rename_to_existing_area_returns_400():
    # Arrange
    module = load_module()

    event = {
        "body": json.dumps({
            "original_name": AREA_DATA[0]["name"],
            "new_name": AREA_DATA[1]["name"],
        })
    }

    # Act
    response = module.update_area(event, None)

    # Assert
    # This should fail until duplicate-name validation is implemented.
    assert response["statusCode"] == 400

    body = json.loads(response["body"])

    assert "Already found area" in body["error"]

def test_exception_returns_500(monkeypatch):
    module = load_module()

    def raise_error(*args, **kwargs):
        raise RuntimeError("boom")

    monkeypatch.setattr(module.area_table, "put_item", raise_error)

    original_name = AREA_DATA[0]["name"]

    event = {
        "body": json.dumps({
            "original_name": original_name,
            "trail_ids": [11, 22, 33],
        })
    }

    # Act
    response = module.update_area(event, None)

    assert response["statusCode"] == 500

    body = json.loads(response["body"])

    assert "Internal server error" in body["error"]