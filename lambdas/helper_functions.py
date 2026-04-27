from datetime import datetime, timedelta
from zoneinfo import ZoneInfo
from decimal import Decimal
import boto3
import os
from boto3.dynamodb.conditions import Key, Attr

dynamodb = boto3.resource('dynamodb')

device_trail_log_hour_table = dynamodb.Table(os.environ.get("DEVICE_TRAIL_LOG_HOUR_TABLE", "local_trailplanner_device_trail_hour_table"))
device_trail_log_day_table = dynamodb.Table(os.environ.get("DEVICE_TRAIL_LOG_DAY_TABLE", "local_trailplanner_device_trail_day_table"))
device_trail_log_week_table = dynamodb.Table(os.environ.get("DEVICE_TRAIL_LOG_WEEK_TABLE", "local_trailplanner_device_trail_week_table"))
device_trail_log_month_table = dynamodb.Table(os.environ.get("DEVICE_TRAIL_LOG_MONTH_TABLE", "local_trailplanner_device_trail_month_table"))
trail_table = dynamodb.Table(os.environ.get("TRAIL_TABLE", "local_trailplanner_trail_table"))
device_table = dynamodb.Table(os.environ.get("DEVICE_TABLE", "local_trailplanner_device_table"))
device_trail_table = dynamodb.Table(os.environ.get("DEVICE_TRAIL_TABLE", "local_trailplanner_device_trail_table"))
area_table = dynamodb.Table(os.environ.get("AREA_TABLE", "local_trailplanner_area_table"))

table_time_map = {
    "hour":  device_trail_log_hour_table,
    "day":   device_trail_log_day_table,
    "week":  device_trail_log_week_table,
    "month": device_trail_log_month_table,
    "year": device_trail_log_month_table
}


s3_client = boto3.client('s3')
csv_bucket = os.environ.get("TRAIL_CSV_BUCKET")

cognito = boto3.client('cognito-idp')
COGNITO_USER_POOL_ID = os.environ.get("COGNITO_USER_POOL_ID")
user_groups = {"user": 0, "trail_manager": 1, "admin": 2, "root_admin": 3}

def convert_decimals(obj):
    if isinstance(obj, list):
        return [convert_decimals(i) for i in obj]
    elif isinstance(obj, dict):
        return {k: convert_decimals(v) for k, v in obj.items()}
    elif isinstance(obj, Decimal):
        return float(obj) if float(obj) % 1 > 0 else int(obj)
    else:
        return obj


def timestamp_conversion(timestamp, time_increment):
    """
    Convert timestamp back to start of day/week/month as need be for higher grade time tables
    :param timestamp: unix timestamp of current time
    :param time_increment: string of day/week/month to convert it to
    :return: timestamp of the start of that period, none if invalid time increment
    """
    dt_timestamp = datetime.fromtimestamp(timestamp, tz=ZoneInfo("America/New_York"))
    if time_increment == "hour":
        return int(dt_timestamp.replace(minute=0, second=0, microsecond=0).timestamp())
    elif time_increment == "day":
        return int(dt_timestamp.replace(hour=0, minute=0, second=0, microsecond=0).timestamp())
    elif time_increment == "week":
        monday = dt_timestamp - timedelta(days=dt_timestamp.weekday())
        return int(monday.replace(hour=0, minute=0, second=0, microsecond=0).timestamp())
    elif time_increment == "month":
        return int(dt_timestamp.replace(day=1, hour=0, minute=0, second=0, microsecond=0).timestamp())
    return None

def get_next_trail_id() -> int:
    print("Retrieving next trail_id")
    # Get all existing trails to find next available ID
    try:
        resp = trail_table.scan()
        existing_trails = resp.get("Items", [])
        if existing_trails:
            existing_ids = [int(t.get("id", 0)) for t in existing_trails]
            new_trail_id = max(existing_ids, default=0) + 1
        else:
            new_trail_id = 1
    except Exception as e:
        print(f"Error finding max trail_id, starting with 1. Exception: {e}")
        # If scan fails, start with ID 1
        new_trail_id = 1

    return new_trail_id

def get_next_device_id() -> int:
    print("Retrieving next device_id")
    # Get all existing devices to find next available ID
    try:
        resp = device_table.scan()
        existing_devices = resp.get("Items", [])
        if existing_devices:
            existing_ids = [int(d.get("id", 0)) for d in existing_devices]
            new_device_id = max(existing_ids, default=0) + 1
        else:
            new_device_id = 1
    except Exception as e:
        print(f"Error finding max device_id, starting with 1. Exception: {e}")
        # If scan fails, start with ID 1
        new_device_id = 1

    return new_device_id

def get_next_device_trail_id() -> int:
    print("Retrieving next device_trail_id")
    # Get all existing device_trails to find next available ID
    try:
        resp = device_trail_table.scan()
        existing_device_trails = resp.get("Items", [])
        if existing_device_trails:
            existing_ids = [int(dt.get("id", 0)) for dt in existing_device_trails]
            new_device_trail_id = max(existing_ids, default=0) + 1
        else:
            new_device_trail_id = 1
    except Exception as e:
        print(f"Error finding max device_trail_id, starting with 1. Exception: {e}")
        # If scan fails, start with ID 1
        new_device_trail_id = 1

    return new_device_trail_id

def get_device_trail_id(device_id, trail_id=None):
    """
    given the device id get the devicetrail id that we need for the time entries
    :param device_id: device id
    :param trail_id: trail id, optional but useful to prevent issues.
    :return: devicetrail id
    """
    if trail_id is None:
        items = device_trail_table.query(
            KeyConditionExpression=Key("device_id").eq(device_id),
            ScanIndexForward=False,
            Limit=1
        ).get("Items", [])
    else:
        items = device_trail_table.query(
            KeyConditionExpression=Key("device_id").eq(device_id),
            FilterExpression=Attr("trail_id").eq(trail_id),
            ScanIndexForward=False,
            Limit=1
        ).get("Items", [])
    if not items:
        raise ValueError(f"No device trail association with device id {device_id}, trail_id={trail_id} found")
    return int(items[0]["id"]), int(items[0]["trail_id"])  # just return the ids, dont need all that


def cors_headers():
    return {
        "Access-Control-Allow-Origin": "*",
        "Access-Control-Allow-Methods": "GET,POST,PUT,DELETE,OPTIONS",
        "Access-Control-Allow-Headers": "Content-Type,Authorization"
    }