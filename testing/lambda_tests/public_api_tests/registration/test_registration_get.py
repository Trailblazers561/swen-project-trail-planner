import importlib
import json
from testing.lambda_tests.test_data import REGISTRATION_DATA


def load_module():
    """
    Import (or reload) the Lambda after Moto has created the mocked AWS
    resources. This ensures the module's global DynamoDB objects point at
    Moto instead of real AWS.
    """
    # DO NOT IMPORT THE FUNCTION UP TOP, IMPORT IT IN THIS FUNCTION
    module = importlib.import_module("lambdas.public_api.registration.registration_get")
    return importlib.reload(module)


def test_get_all_registrations():
    # Arrange
    module = load_module()

    event = {
        "queryStringParameters": {}
    }

    # Act
    response = module.get_registrations(event, None)

    # Assert
    assert response["statusCode"] == 200

    body = json.loads(response["body"])
    assert len(body) == len(REGISTRATION_DATA)

    for actual, expected in zip(body, REGISTRATION_DATA):
        assert actual["registration_id"] == expected["registration_id"]
        assert actual["device_id"] == expected["device_id"]
        assert actual["date_registered"] == expected["date_registered"]
        assert actual["cert_time_to_live"] == expected["cert_time_to_live"]

        assert "device" in actual
        assert actual["device"]["id"] == expected["device_id"]


def test_get_specific_registration():
    # Arrange
    module = load_module()

    event = {
        "queryStringParameters": {
            "registration_id": "1"
        }
    }

    # Act
    response = module.get_registrations(event, None)

    # Assert
    assert response["statusCode"] == 200

    body = json.loads(response["body"])

    assert len(body) == 1

    registration = body[0]

    assert registration["registration_id"] == 1
    assert registration["device_id"] == 1
    assert "device" in registration
    assert registration["device"]["id"] == 1


def test_unknown_registration():
    # Arrange
    module = load_module()

    event = {
        "queryStringParameters": {
            "registration_id": "999999"
        }
    }

    # Act
    response = module.get_registrations(event, None)

    # Assert
    assert response["statusCode"] == 200

    body = json.loads(response["body"])

    assert body == []


def test_registration_id_not_integer():
    # Arrange
    module = load_module()

    event = {
        "queryStringParameters": {
            "registration_id": "abc"
        }
    }

    # Act
    response = module.get_registrations(event, None)

    # Assert
    assert response["statusCode"] == 400

    body = json.loads(response["body"])

    assert "invalid literal for int()" in body["error"]


def test_registration_id_float():
    # Arrange
    module = load_module()

    event = {
        "queryStringParameters": {
            "registration_id": "1.5"
        }
    }

    # Act
    response = module.get_registrations(event, None)

    # Assert
    assert response["statusCode"] == 400


def test_registration_id_empty_string():
    # Arrange
    module = load_module()

    event = {
        "queryStringParameters": {
            "registration_id": ""
        }
    }

    # Act
    response = module.get_registrations(event, None)

    # Assert
    assert response["statusCode"] == 400


def test_missing_query_parameters():
    # Arrange
    module = load_module()

    # Act
    response = module.get_registrations({}, None)

    # Assert
    assert response["statusCode"] == 200

    body = json.loads(response["body"])

    len(body) == len(REGISTRATION_DATA)


def test_none_query_parameters():
    # Arrange
    module = load_module()

    event = {
        "queryStringParameters": None
    }

    # Act
    response = module.get_registrations(event, None)

    # Assert
    assert response["statusCode"] == 200

    body = json.loads(response["body"])

    len(body) == len(REGISTRATION_DATA)

def test_exception_returns_500(monkeypatch):
    module = load_module()

    def raise_error(*args, **kwargs):
        raise RuntimeError("boom")

    monkeypatch.setattr(module.registration_table, "scan", raise_error)

    response = module.get_registrations({}, None)

    assert response["statusCode"] == 500

    body = json.loads(response["body"])

    assert "Internal server error" in body["error"]