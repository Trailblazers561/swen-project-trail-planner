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
    module = importlib.import_module("lambdas.public_api.areas.areas_post")
    return importlib.reload(module)

def test_create_area():
    # Arrange
    module = load_module()

    event = {
        "body": json.dumps({
            "name": "New Area",
            "trail_ids": [1, 2, 3]
        })
    }

    # Act
    response = module.create_area(event, None)

    # Assert
    assert response["statusCode"] == 200

    body = json.loads(response["body"])

    assert body["message"] == "Area created successfully"

    created = module.area_table.get_item(
        Key={"name": "New Area"}
    ).get("Item")

    assert created["name"] == "New Area"
    assert created["trail_ids"] == [1, 2, 3]

def test_create_area_reassigns_trails():
    # Arrange
    module = load_module()

    original_area = AREA_DATA[0]["name"]

    # Give the existing area some trails
    module.area_table.put_item(
        Item={
            "name": original_area,
            "trail_ids": [1, 2, 3],
        }
    )

    event = {
        "body": json.dumps({
            "name": "New Area",
            "trail_ids": [2, 4],
        })
    }

    # Act
    response = module.create_area(event, None)

    # Assert
    assert response["statusCode"] == 200

    original = module.area_table.get_item(
        Key={"name": original_area}
    )["Item"]

    new = module.area_table.get_item(
        Key={"name": "New Area"}
    )["Item"]

    assert original["trail_ids"] == [1, 3]
    assert new["trail_ids"] == [2, 4]

def test_create_area_accepts_dict_body():
    # Arrange
    module = load_module()

    event = {
        "body": {
            "name": "Dictionary Body",
            "trail_ids": [10]
        }
    }

    # Act
    response = module.create_area(event, None)

    # Assert
    assert response["statusCode"] == 200

    created = module.area_table.get_item(
        Key={"name": "Dictionary Body"}
    ).get("Item")

    assert created["trail_ids"] == [10]


def test_duplicate_area_returns_400():
    # Arrange
    module = load_module()

    event = {
        "body": json.dumps({
            "name": AREA_DATA[0]["name"]
        })
    }

    # Act
    response = module.create_area(event, None)

    # Assert
    assert response["statusCode"] == 400

    body = json.loads(response["body"])

    assert "Already found area" in body["error"]


def test_missing_name_returns_400():
    # Arrange
    module = load_module()

    event = {
        "body": json.dumps({})
    }

    # Act
    response = module.create_area(event, None)

    # Assert
    assert response["statusCode"] == 400

    body = json.loads(response["body"])

    assert body["error"] == "Missing required field: name"


def test_invalid_trail_ids_returns_400():
    # Arrange
    module = load_module()

    event = {
        "body": json.dumps({
            "name": "Bad Area",
            "trail_ids": ["abc", 1]
        })
    }

    # Act
    response = module.create_area(event, None)

    # Assert
    assert response["statusCode"] == 400

    body = json.loads(response["body"])

    assert body["error"] == "Invalid trail_ids format"


def test_empty_trail_ids_is_allowed():
    # Arrange
    module = load_module()

    event = {
        "body": json.dumps({
            "name": "Empty Trails",
            "trail_ids": []
        })
    }

    # Act
    response = module.create_area(event, None)

    # Assert
    assert response["statusCode"] == 200

    created = module.area_table.get_item(
        Key={"name": "Empty Trails"}
    ).get("Item")

    assert created["trail_ids"] == []


def test_invalid_json_returns_500():
    # Arrange
    module = load_module()

    event = {
        "body": "{not valid json"
    }

    # Act
    response = module.create_area(event, None)

    # Assert
    assert response["statusCode"] == 400

    body = json.loads(response["body"])

    assert "Expecting property name enclosed in double quotes" in body["error"]