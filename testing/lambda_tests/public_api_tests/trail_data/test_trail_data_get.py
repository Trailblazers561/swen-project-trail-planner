from testing.lambda_tests.test_data import DAY_LOG_DATA, DEVICE_TRAIL_DATA, MONTH_LOG_DATA
import importlib
import json
from datetime import datetime

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
            "trail_id": ["1"],
        },
    }

    #Act
    response = module.get_trail_data(event, None)

    #Assert
    assert response["statusCode"] == 200

    body = json.loads(response["body"])

    # Required fields exist
    for row in body:
        assert "device_trail_id" in row
        assert "start" in row
        assert "count" in row
        assert "device_id" in row
        assert "trail_id" in row

    # Ensure all results belong to trail 1
    assert all(row["trail_id"] == 1 for row in body)

def test_get_partial_trail():
    #Arrange
    module = load_module()

    start = datetime.fromisoformat("2026-01-10T00:00:00")
    end = datetime.fromisoformat("2026-03-15T00:00:00")

    event = {
        "queryStringParameters": {
            "start_time": start.isoformat(),
            "end_time": end.isoformat(),
            "granularity": "month",
        },
        "multiValueQueryStringParameters": {
            "trail_id": ["1"],
        },
    }

    #Act
    response = module.get_trail_data(event, None)

    #Assert
    assert response["statusCode"] == 200

    body = json.loads(response["body"])
    body.sort(key=lambda x: x["start"]) #put the returned data in chronological order

    jan_end = datetime(2026, 2, 1).timestamp()
    feb_start = jan_end
    feb_end = datetime(2026, 3, 1).timestamp()
    mar_start = feb_end


    expected_jan = sum(
        row["count"]
        for row in DAY_LOG_DATA
        if row.get("device_trail_id") == 1
        and start.timestamp() <= row["start"] < jan_end
    )

    expected_feb = next(
        row["count"]
        for row in MONTH_LOG_DATA
        if row.get("device_trail_id") == 1
        and row["start"] == feb_start
    )

    expected_mar = sum(
        row["count"]
        for row in DAY_LOG_DATA
        if row.get("device_trail_id") == 1
        and mar_start <= row["start"] <= end.timestamp()
    )

    assert body[0]["trail_id"] == 1
    assert body[0]["count"] == expected_jan

    assert body[1]["trail_id"] == 1
    assert body[1]["count"] == expected_feb

    assert body[2]["trail_id"] == 1
    assert body[2]["count"] == expected_mar


def test_error_for_no_trail_id():
    #Arrange
    module = load_module()

    event = {
        "queryStringParameters": {
            "start_time": "...",
            "end_time": "...",
            "granularity": "day",
        },
        "multiValueQueryStringParameters": {
        },
    }

    #Act
    response = module.get_trail_data(event, None)

    #Assert
    assert response["statusCode"] == 400

def test_error_for_no_time_range():
    #Arrange
    module = load_module()

    event = {
        "queryStringParameters": {
            "granularity": "day",
        },
        "multiValueQueryStringParameters": {
            "trail_id": ["1"]
        },
    }

    #Act
    response = module.get_trail_data(event, None)

    #Assert
    assert response["statusCode"] == 400

def test_error_for_invalid_trail_id():
    #Arrange
    module = load_module()

    event = {
        "queryStringParameters": {
            "start_time": "2026-01-01T00:00:00",
            "end_time": "2026-01-02T00:00:00",
            "granularity": "day",
        },
        "multiValueQueryStringParameters": {
            "trail_id": ["abc"]
        },
    }

    #Act
    response = module.get_trail_data(event, None)

    #Assert
    assert response["statusCode"] == 400

def test_trail_filter():
    #Arrange
    module = load_module()

    event = {
        "queryStringParameters": {
            "start_time": "2026-01-01T00:00:00",
            "end_time": "2026-01-02T00:00:00",
            "granularity": "day",
        },
        "multiValueQueryStringParameters": {
            "trail_id": ["1"],
        },
    }

    #Act
    response = module.get_trail_data(event, None)

    body = json.loads(response["body"])
    #Assert
    assert all(row["trail_id"] == 1 for row in body)

def test_time_range_filter():
    # Arrange
    module = load_module()

    start_time = "2026-01-01T00:00:00"
    end_time = "2026-01-02T00:00:00"

    event = {
        "queryStringParameters": {
            "start_time": start_time,
            "end_time": end_time,
            "granularity": "day",
        },
        "multiValueQueryStringParameters": {
            "trail_id": ["1"],
        },
    }

    # Act
    response = module.get_trail_data(event, None)

    # Assert
    assert response["statusCode"] == 200

    body = json.loads(response["body"])

    assert len(body) == 2
    assert body[0]["start"] < body[1]["start"]

def test_empty_data():
    #Arrange
    module = load_module()

    event = {
        "queryStringParameters": {
            "start_time": "1990-01-01T00:00:00",
            "end_time": "1990-01-02T00:00:00",
            "granularity": "day",
        },
        "multiValueQueryStringParameters": {
            "trail_id": ["1"],
        },
    }

    #Act
    response = module.get_trail_data(event, None)

    #Assert
    assert response["statusCode"] == 200

    body = json.loads(response["body"])

    assert body == []

def test_multi_trail():
    #Arrange
    module = load_module()

    event = {
        "queryStringParameters": {
            "start_time": "2026-01-01T00:00:00",
            "end_time": "2026-01-02T00:00:00",
            "granularity": "day",
        },
        "multiValueQueryStringParameters": {
            "trail_id": ["1", "2"],
        },
    }

    #Act
    response = module.get_trail_data(event, None)

    #Assert
    assert response["statusCode"] == 200

    body = json.loads(response["body"])

    assert len(body) > 0
    assert all(row["trail_id"] in (1, 2) for row in body)

def test_exception_returns_500(monkeypatch):
    #Arrange
    module = load_module()

    event = {
        "queryStringParameters": {
            "start_time": "2026-01-01T00:00:00",
            "end_time": "2026-01-02T00:00:00",
        },
        "multiValueQueryStringParameters": {
            "trail_id": ["1"],
        },
    }

    def raise_error(*args, **kwargs):
        raise RuntimeError("boom")

    monkeypatch.setattr(module.device_trail_table, "query", raise_error)

    #Act
    response = module.get_trail_data(event, None)

    #Assert
    assert response["statusCode"] == 500

    body = json.loads(response["body"])
    assert "Internal server error" in body["error"]