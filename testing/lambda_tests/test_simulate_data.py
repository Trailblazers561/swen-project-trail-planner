import importlib

import boto3
import pytest

def load_module():
    """
    Import (or reload) the Lambda after Moto has created the mocked AWS
    resources. This ensures the module's global DynamoDB objects point at
    Moto instead of real AWS.
    """
    # DO NOT IMPORT THE FUNCTION UP TOP, IMPORT IT IN THIS FUNCTION
    module = importlib.import_module("lambdas.simulate_data")
    return importlib.reload(module)

def test_simulate_data_success():
    # Arrange
    module = load_module()

    event = {
        "time": "2025-01-01T12:00:00+00:00"
    }

    module.simulate_data(event, None)

    # Act
    response = module.log_day_table.scan()

    # Assert
    assert response["Count"] > 0
    assert module.device_log_table.scan()["Count"] > 0
    assert module.log_hour_table.scan()["Count"] > 0

def test_missing_time():
    module = load_module()

    with pytest.raises(KeyError):
        module.simulate_data({}, None)

def test_invalid_time():
    module = load_module()

    with pytest.raises(KeyError):
        module.simulate_data({}, None)

def test_create_trail():
    # Arrange
    module = load_module()

    new_id = module.create_trail("Test Trail")

    # Act
    response = module.trail_table.get_item(
        Key={"id": new_id}
    )

    item = response["Item"]

    # Assert
    assert item["name"] == "Test Trail"
    assert item["id"] == new_id

def test_create_device_trail():
    # Arrange
    module = load_module()

    device_trail_id, device_id = module.create_device_trail(999)

    # Act
    device = module.device_table.get_item(
        Key={"id": device_id}
    )["Item"]

    # Assert
    assert device["id"] == device_id

    response = module.device_trail_table.scan()

    assert response["Count"] > 0

def test_log_hour():
    # Arrange
    module = load_module()

    module.log_hour(1, 1000, 25)

    # Act
    response = module.log_hour_table.get_item(
        Key={
            "device_trail_id": 1,
            "start": 1000
        }
    )

    # Assert
    assert response["Item"]["count"] == 25

def test_log_day():
    # Arrange
    module = load_module()

    module.log_day(1, 1000, 40)

    # Act
    response = module.log_day_table.get_item(
        Key={
            "device_trail_id": 1,
            "start": 1000
        }
    )

    # Assert
    assert response["Item"]["count"] == 40

def test_log_week():
    # Arrange
    module = load_module()

    module.log_week(1, 1000, 50)

    # Act
    response = module.log_week_table.get_item(
        Key={
            "device_trail_id": 1,
            "start": 1000
        }
    )

    # Assert
    assert response["Item"]["count"] == 50

def test_log_month():
    # Arrange
    module = load_module()

    module.log_month(1, 1000, 75)

    # Act
    response = module.log_month_table.get_item(
        Key={
            "device_trail_id": 1,
            "start": 1000
        }
    )

    # Assert
    assert response["Item"]["count"] == 75

def test_log_log():
    # Arrange
    module = load_module()

    module.log_log(1, 30, 95)

    # Act
    response = module.device_log_table.query(
        # Assert
        KeyConditionExpression=boto3.dynamodb.conditions.Key("device_id").eq(1)
    )

    assert response["Count"] >= 1

def test_forecast_sunny():
    # Arrange
    module = load_module()

    # Act
    result = module.get_forecast_multiplier("Sunny")

    # Assert
    assert result == 1.3

def test_forecast_rain():
    # Arrange
    module = load_module()

    # Act
    result = module.get_forecast_multiplier("Rain")

    # Assert
    assert result == 0.6


def test_forecast_unknown():
    # Arrange
    module = load_module()

    # Act
    result = module.get_forecast_multiplier("Unknown")

    # Assert
    assert result == 1.0

def test_temp_multiplier_70():
    # Arrange
    module = load_module()

    # Act
    result = module.get_temp_multiplier(70)

    # Assert
    assert result == 1.0

def test_temp_multiplier_hot():
    # Arrange
    module = load_module()

    # Act
    result = module.get_temp_multiplier(100)

    # Assert
    assert result < 1

def test_temp_multiplier_cold():
    # Arrange
    module = load_module()

    # Act
    result = module.get_temp_multiplier(10)

    # Assert
    assert result < 1

def test_nth_weekday():
    # Arrange
    module = load_module()

    # Act
    result = module.nth_weekday(2025, 1, 0, 3)

    # Assert
    assert result == date(2025, 1, 20)

from datetime import date

def test_holiday_multiplier():
    # Arrange
    module = load_module()

    holiday = date(2025, 7, 4)

    # Act
    result = module.get_holiday_multiplier(holiday)

    # Assert
    assert result == 2.3

from datetime import date

def test_non_holiday_multiplier():
    # Arrange
    module = load_module()

    day = date(2025, 8, 20)

    # Act
    result = module.get_holiday_multiplier(day)

    # Assert
    assert result == 1.0

def test_create_trail_empty_table(monkeypatch):
    # Arrange
    module = load_module()

    monkeypatch.setattr(
        module.trail_table,
        "scan",
        lambda: {"Items": []}
    )

    # Act
    new_id = module.create_trail("Brand New")

    # Assert
    assert new_id == 1

def test_exception_returns_500(monkeypatch):
    module = load_module()

    def raise_error(*args, **kwargs):
        raise RuntimeError("boom")

    monkeypatch.setattr(module, "get_weather_multiplier", raise_error)
    