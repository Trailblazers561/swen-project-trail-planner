import importlib
import json

def load_module():
    """
    Import (or reload) the Lambda after Moto has created the mocked AWS
    resources. This ensures the module's global DynamoDB objects point at
    Moto instead of real AWS.
    """
    # DO NOT IMPORT THE FUNCTION UP TOP, IMPORT IT IN THIS FUNCTION
    module = importlib.import_module("lambdas.public_api.heatmap.heatmap_get")
    return importlib.reload(module)

def test_absolute_algorithm_success():
    #Arrange
    module = load_module()

    event = {
        "queryStringParameters": {
            "start_time": "2026-01-01T00:00:00",
            "end_time": "2026-01-31T23:59:59",
            "algorithm": "absolute"
        },
        "multiValueQueryStringParameters": {
            "trail_id": ["1", "2"]
        }
    }

    # Act
    response = module.get_heatmap_data(event, None)

    # Assert
    assert response["statusCode"] == 200

    body = json.loads(response["body"])

    assert isinstance(body, dict)

    assert isinstance(body["1"], (int, float))
    assert isinstance(body["2"], (int, float))

def test_missing_trail_id():
    #Arrange
    module = load_module()

    event = {
        "queryStringParameters": {
            "start_time": "2025-01-01T00:00:00",
            "end_time": "2025-01-02T00:00:00"
        },
        "multiValueQueryStringParameters": {}
    }

    # Act
    response = module.get_heatmap_data(event, None)

    # Assert
    assert response["statusCode"] == 400
    assert "trail_id" in json.loads(response["body"])["error"]

def test_missing_start_time():
    # Arrange
    module = load_module()

    event = {
        "queryStringParameters": {
            "end_time": "2025-01-02T00:00:00"
        },
        "multiValueQueryStringParameters": {
            "trail_id": ["1"]
        }
    }

    # Act
    response = module.get_heatmap_data(event, None)

    # Assert
    assert response["statusCode"] == 400

def test_missing_end_time():
    # Arrange
    module = load_module()

    event = {
        "queryStringParameters": {
            "start_time": "2025-01-01T00:00:00"
        },
        "multiValueQueryStringParameters": {
            "trail_id": ["1"]
        }
    }

    # Act
    response = module.get_heatmap_data(event, None)

    # Assert
    assert response["statusCode"] == 400

def test_invalid_trail_id_non_numeric():
    # Arrange
    module = load_module()

    event = {
        "queryStringParameters": {
            "start_time": "2025-01-01T00:00:00",
            "end_time": "2025-01-02T00:00:00"
        },
        "multiValueQueryStringParameters": {
            "trail_id": ["abc", "1"]
        }
    }

    # Act
    response = module.get_heatmap_data(event, None)

    # Assert
    assert response["statusCode"] == 400

def test_invalid_algorithm():
    # Arrange
    module = load_module()

    event = {
        "queryStringParameters": {
            "start_time": "2025-01-01T00:00:00",
            "end_time": "2025-01-02T00:00:00",
            "algorithm": "wrong_algo"
        },
        "multiValueQueryStringParameters": {
            "trail_id": ["1"]
        }
    }

    # Act
    response = module.get_heatmap_data(event, None)

    # Assert
    assert response["statusCode"] == 400

def test_end_time_before_start_time():
    # Arrange
    module = load_module()

    event = {
        "queryStringParameters": {
            "start_time": "2025-01-05T00:00:00",
            "end_time": "2025-01-01T00:00:00"
        },
        "multiValueQueryStringParameters": {
            "trail_id": ["1"]
        }
    }

    # Act
    response = module.get_heatmap_data(event, None)

    # Assert
    assert response["statusCode"] == 200

    body = json.loads(response["body"])
    assert isinstance(body, dict)


def test_invalid_datetime_format():
    # Arrange
    module = load_module()

    event = {
        "queryStringParameters": {
            "start_time": "not-a-date",
            "end_time": "also-bad"
        },
        "multiValueQueryStringParameters": {
            "trail_id": ["1"]
        }
    }

    # Act
    response = module.get_heatmap_data(event, None)

    # Assert
    assert response["statusCode"] == 400

def test_exception_returns_500(monkeypatch):
    module = load_module()

    def raise_error(*args, **kwargs):
        raise RuntimeError("boom")

    monkeypatch.setattr(module.device_trail_table, "query", raise_error)

    event = {
        "queryStringParameters": {
            "start_time": "2025-01-01T00:00:00",
            "end_time": "2025-01-02T00:00:00"
        },
        "multiValueQueryStringParameters": {
            "trail_id": ["1"]
        }
    }

    response = module.get_heatmap_data(event, None)

    assert response["statusCode"] == 500

    body = json.loads(response["body"])

    assert "Internal server error" in body["error"]