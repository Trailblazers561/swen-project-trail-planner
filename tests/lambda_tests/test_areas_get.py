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
    print("AREAS: ", response)

    # Assert
    assert response["statusCode"] == 200

    body = json.loads(response["body"])

    assert len(body) == 1

    names = {area["name"] for area in body}

    assert names == {"Testing Area"}

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

    assert len(body) == 1
    assert body[0]["name"] == "Old Area"


def test_get_specific_areas(aws):
    # Arrange
    area_table = aws["area"]

    area_table.put_item(Item={"name": "High Peaks"})
    area_table.put_item(Item={"name": "Dix"})
    area_table.put_item(Item={"name": "Sentinel Range"})

    module = load_module()

    event = {
        "queryStringParameters": {},
        "multiValueQueryStringParameters": {
            "name": [
                "High Peaks",
                "Dix",
            ]
        },
    }

    # Act
    response = module.get_areas(event, None)

    # Assert
    assert response["statusCode"] == 200

    body = json.loads(response["body"])

    names = {area["name"] for area in body}

    assert names == {"High Peaks", "Dix"}


def test_unknown_area_returns_empty_list(aws):
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


def test_empty_database_returns_empty_list(aws):
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
    assert json.loads(response["body"]) == []