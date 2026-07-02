from lambda_config import update_sys_path
update_sys_path()

import importlib
import json

import boto3

def load_module():
    """
    Import (or reload) the Lambda after Moto has created the mocked AWS
    resources. This ensures the module's global DynamoDB objects point at
    Moto instead of real AWS.
    """
    module = importlib.import_module("lambdas.public_api.areas.areas_get")
    return importlib.reload(module)


def test_get_all_active_areas():
    # Arrange
    module = load_module()

    event = {
        "queryStringParameters": {},
        "multiValueQueryStringParameters": {},
    }

    # Act
    response = module.get_areas(event, None)

    # Assert
    assert response["statusCode"] == 200

    body = json.loads(response["body"])

    assert len(body) == 4

    names = {area["name"] for area in body}
    print("AREAS: ", names)

    assert names == {"Adirondack Park", "Testing Area", "High Peaks Wilderness", "Giant Mountain Wilderness"}

def test_get_only_retired_areas():
    module = load_module()

    event = {
        "queryStringParameters": {
            "retired": ""
        },
        "multiValueQueryStringParameters": {},
    }

    # Act
    response = module.get_areas(event, None)

    # Assert
    assert response["statusCode"] == 200

    body = json.loads(response["body"])

    assert len(body) == 0
    # commented out because I want to add more in the future
    # assert body[0]["name"] == "Old Area"


def test_get_specific_areas():
    # Arrange
    module = load_module()

    event = {
        "queryStringParameters": {},
        "multiValueQueryStringParameters": {
            "name": [
                "Adirondack Park",
                "Testing Area",
            ]
        },
    }

    # Act
    response = module.get_areas(event, None)

    # Assert
    assert response["statusCode"] == 200

    body = json.loads(response["body"])

    names = {area["name"] for area in body}

    assert names == {"Adirondack Park", "Testing Area"}


def test_unknown_area_returns_empty_list():
    # Arrange
    module = load_module()

    event = {
        "queryStringParameters": {},
        "multiValueQueryStringParameters": {
            "name": [
                "Does Not Exist"
            ]
        },
    }

    # Act
    response = module.get_areas(event, None)

    # Assert
    assert response["statusCode"] == 200
    assert json.loads(response["body"]) == []