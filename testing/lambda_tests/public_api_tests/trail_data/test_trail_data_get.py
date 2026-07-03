from testing.lambda_tests.test_data import TRAIL_DATA

import importlib
import json

def load_module():
    """
    Import (or reload) the Lambda after Moto has created the mocked AWS
    resources. This ensures the module's global DynamoDB objects point at
    Moto instead of real AWS.
    """
    # DO NOT IMPORT THE FUNCTION UP TOP, IMPORT IT IN THIS FUNCTION
    module = importlib.import_module("lambdas.public_api.trail_data.trail_data_get")
    return importlib.reload(module)


def test_get_single_trail():
    #Arrange
    module = load_module()

    event = {
    "queryStringParameters": {
        "start_time": "2026-01-01T00:00:00",
        "end_time": "2026-01-02T00:00:00",
        "granularity": "day",
    },
    "multiValueQueryStringParameters": {
        "trail_id": ["8"],
    },
}

    #Act
    response = module.get_trail_data(event, None)

    #Assert
    assert response["statusCode"] == 200

    body = json.loads(response["body"])

    assert len(body) == 4

    # Pull all area names from test_data.py
    expected_names = {area["name"] for area in TRAIL_DATA}
    names = {area["name"] for area in body}

    assert names == expected_names
