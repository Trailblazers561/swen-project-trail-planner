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
    module = importlib.import_module("lambdas.public_api.areas.areas_delete")
    return importlib.reload(module)


def test_retire_area():
    # Arrange
    module = load_module()

    name = AREA_DATA[0]["name"]

    event = {
        "body": json.dumps({
            "name": name,
        })
    }

    # Act
    response = module.retire_area(event, None)

    # Assert
    assert response["statusCode"] == 200

    body = json.loads(response["body"])

    assert body["message"] == "Area retired successfully"

    retired = module.area_table.get_item(
        Key={"name": name}
    )["Item"]

    assert retired["retired"] is True
    assert retired["trail_ids"] == []


def test_retire_area_accepts_dict_body():
    # Arrange
    module = load_module()

    name = AREA_DATA[0]["name"]

    event = {
        "body": {
            "name": name,
        }
    }

    # Act
    response = module.retire_area(event, None)

    # Assert
    assert response["statusCode"] == 200


def test_missing_name_returns_400():
    # Arrange
    module = load_module()

    event = {
        "body": json.dumps({})
    }

    # Act
    response = module.retire_area(event, None)

    # Assert
    assert response["statusCode"] == 400

    body = json.loads(response["body"])

    assert body["error"] == "Missing required field: name"


def test_unknown_area_returns_400():
    # Arrange
    module = load_module()

    event = {
        "body": json.dumps({
            "name": "Does Not Exist",
        })
    }

    # Act
    response = module.retire_area(event, None)

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
    response = module.retire_area(event, None)

    # Assert
    assert response["statusCode"] == 400

    body = json.loads(response["body"])

    assert body["error"]

def test_retire_area_preserves_other_fields():
    module = load_module()

    module.area_table.put_item(
        Item={
            "name": "Testing Area",
            "trail_ids": [1, 2],
            "description": "Important",
        }
    )

    response = module.retire_area({
        "body": json.dumps({"name": "Testing Area"})
    }, None)

    assert response["statusCode"] == 200

    item = module.area_table.get_item(
        Key={"name": "Testing Area"}
    )["Item"]

    assert item["description"] == "Important"
    assert item["trail_ids"] == []
    assert item["retired"] is True