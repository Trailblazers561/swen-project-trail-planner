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
    # DO NOT IMPORT THE FUNCTION UP TOP, IMPORT IT IN THIS FUNCTION
    module = importlib.import_module("lambdas.public_api.areas.areas_get")
    return importlib.reload(module)


def test_get_all_active_areas():
    # Arrange
    # THIS IS THE IMPORT STATEMENT - DO THIS FOR EVERY FUNCTION
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

    # Pull all area names from test_data.py
    expected_names = {area["name"] for area in AREA_DATA}
    names = {area["name"] for area in body}

    assert names == expected_names

def test_get_only_retired_areas():
    # Arrange
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

    expected_names = {"Adirondack Park", "Testing Area"}
    names = {area["name"] for area in body}

    assert names == expected_names

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

def test_none_query_parameters():
    module = load_module()

    event = {
        "queryStringParameters": None,
        "multiValueQueryStringParameters": None,
    }

    response = module.get_areas(event, None)

    assert response["statusCode"] == 200

    body = json.loads(response["body"])
    assert len(body) == 4

def test_empty_name_list_returns_all_active():
    module = load_module()

    event = {
        "queryStringParameters": {},
        "multiValueQueryStringParameters": {
            "name": []
        },
    }

    response = module.get_areas(event, None)

    assert response["statusCode"] == 200

    body = json.loads(response["body"])
    assert len(body) == 4

def test_name_lookup_ignores_retired_parameter():
    module = load_module()

    event = {
        "queryStringParameters": {
            "retired": ""
        },
        "multiValueQueryStringParameters": {
            "name": ["Testing Area"]
        },
    }

    response = module.get_areas(event, None)

    assert response["statusCode"] == 200

    body = json.loads(response["body"])

    assert len(body) == 1
    assert body[0]["name"] == "Testing Area"

def test_missing_query_parameters():
    module = load_module()

    response = module.get_areas({}, None)

    assert response["statusCode"] == 200

    body = json.loads(response["body"])
    assert len(body) == 4

def test_value_error_returns_400(monkeypatch):
    module = load_module()

    def raise_error(*args, **kwargs):
        raise ValueError("bad request")

    monkeypatch.setattr(module.area_table, "scan", raise_error)

    response = module.get_areas({}, None)

    assert response["statusCode"] == 400

    body = json.loads(response["body"])
    assert body["error"] == "bad request"

def test_exception_returns_500(monkeypatch):
    module = load_module()

    def raise_error(*args, **kwargs):
        raise RuntimeError("boom")

    monkeypatch.setattr(module.area_table, "scan", raise_error)

    response = module.get_areas({}, None)

    assert response["statusCode"] == 500

    body = json.loads(response["body"])

    assert "Internal server error" in body["error"]