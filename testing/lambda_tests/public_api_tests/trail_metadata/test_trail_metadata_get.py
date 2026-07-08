import importlib
import json

def load_module():
    """
    Import (or reload) the Lambda after Moto has created the mocked AWS
    resources. This ensures the module's global DynamoDB objects point at
    Moto instead of real AWS.
    """
    # DO NOT IMPORT THE FUNCTION UP TOP, IMPORT IT IN THIS FUNCTION
    module = importlib.import_module("lambdas.public_api.trail_metadata.trail_metadata_get")
    return importlib.reload(module)

def test_get_single_metadata():
    #Arrange
    module = load_module()

    event = {
        "queryStringParameters": {
            "retired": "false",
        },
        "multiValueQueryStringParameters": {
            "trail_id": ["1"],
        },
    }

    #Act
    response = module.get_trail_metadata(event, None)

    #Assert
    assert response["statusCode"] == 200

    body = json.loads(response["body"])

    # Ensure returned metadata matches seeded data
    assert len(body) == 1
    assert body[0]["id"] == 1

    assert body[0]["name"] == "Mt. Marcy"

def test_empty_list_for_no_trail_id():
    #Arrange
    module = load_module()

    event = {
        "queryStringParameters": {
            "retired": "false",
        },
        "multiValueQueryStringParameters": {
        },
    }

    #Act
    response = module.get_trail_metadata(event, None)

    #Assert
    assert response["statusCode"] == 200

    body = json.loads(response["body"])

    assert len(body) == 0


def test_error_for_invalid_trail_id():
    #Arrange
    module = load_module()

    event = {
        "queryStringParameters": {
            "retired": "false",
        },
        "multiValueQueryStringParameters": {
            "trail_id": ["test"],
        },
    }

    #Act
    response = module.get_trail_metadata(event, None)

    #Assert
    assert response["statusCode"] == 400
    
    body = json.loads(response["body"])

    assert body["error"] == "Invalid trail_id_list format"

def test_get_retired_trails_works():
    #Arrange
    module = load_module()

    event = {
        "queryStringParameters": {
            "retired": "true",
        },
        "multiValueQueryStringParameters": {
            "trail_id": [],
        },
    }

    #Act
    response = module.get_trail_metadata(event, None)

    #Assert
    assert response["statusCode"] == 200

def test_get_multiple_metadata():
    #Arrange
    module = load_module()

    event = {
        "queryStringParameters": {
            "retired": "false",
        },
        "multiValueQueryStringParameters": {
            "trail_id": ["1", "2"],
        },
    }

    #Act
    response = module.get_trail_metadata(event, None)

    #Assert
    assert response["statusCode"] == 200

    body = json.loads(response["body"])

    # Ensure returned metadata amount matches
    assert len(body) == 2
    

