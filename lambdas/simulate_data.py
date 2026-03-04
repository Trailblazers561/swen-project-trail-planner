import os
import boto3
from boto3.dynamodb.conditions import Key, Attr
import random
from datetime import datetime
from zoneinfo import ZoneInfo

dynamodb = boto3.resource('dynamodb')

# Table references
logs_table = dynamodb.Table(os.environ.get("TRAIL_LOGS_TABLE", "local_TrailDeviceLogs"))
trail_metadata_table = dynamodb.Table(os.environ.get("TRAIL_METADATA_TABLE", "local_TrailMetadata"))
device_metadata_table = dynamodb.Table(os.environ.get("DEVICE_METADATA_TABLE", "local_DeviceMetadata"))
trail_groups_table = dynamodb.Table(os.environ.get("TRAIL_GROUPS_TABLE", "local_TrailGroups"))

# Trails to update, Name: [mean, std_dev]
trails = {
    "Mt. Marcy": [90, 20],
    "Giant Mountain": [50, 12],
    "Poke-O-Moonshine Ranger Trail": [40, 10],
    "Mt. Skylight": [35, 9],
    "Cat Mountain": [30, 8],
    "Bald Peak": [25, 6],
    "Beaver Meadow Trail": [20, 5],
    "Mt. Haystack": [20, 7],
    "Mud Lake": [15, 5],
    "Blueberry Trail": [15, 8]
}

# Hiker Multiplier based on day of the week Monday - Sunday
weekday_modifier = {0: .8, 1: .65, 2: .50, 3: .60, 4: .90, 5: 1.95, 6: 1.6}

seconds_in_day = 24 * 60 * 60

def simulate_data(event, context):
    # Retrieve Timestamp for start of day (EST) when lambda was called
    date = datetime.fromisoformat(event["time"][:10]).replace(tzinfo=ZoneInfo("America/New_York"))
    timestamp = int(date.timestamp())
    for trail, stats in trails.items():
        # Check if trail is in the database, create it if not found
        response = trail_metadata_table.query(
            IndexName="trail_name-index",
            KeyConditionExpression=Key("trail_name").eq(trail)
        )
        if response["Count"] >= 1:
            trail_id = response["Items"][0]["trail_id"]
        else:
            trail_id = create_trail(trail)

        # Check if device for the trail is in the database, create it if not
        response = device_metadata_table.scan(
            FilterExpression=Attr("current_trail_id").eq(trail_id)
        )
        if response["Count"] >= 1:
            device_id = response["Items"][0]["device_id"]
            battery = response["Items"][0]["battery"]
        else:
            device_id = create_device(trail_id)
            battery = 100
        # 1/3 chance to decrement battery
        if (random.random() < 1/3):
            battery = battery - 1

        # Determine amount of hikers for the day
        hikers = max(int(random.normalvariate(*stats) * weekday_modifier[date.weekday()]), 0)
        # Space timestamps across the day and log them
        interval = int(seconds_in_day / (hikers + 1))
        temp_timestamp = timestamp + int(interval/2)
        for i in range(hikers):
            add_log(trail_id, device_id, battery, temp_timestamp)
            temp_timestamp += interval

        # Update device to reflect updated battery and last_update
        update_device(device_id, battery, temp_timestamp)

def create_trail(trail: str) -> int:
    # Get all existing trails to find next available ID
    try:
        resp = trail_metadata_table.scan()
        existing_trails = resp.get("Items", [])
        if existing_trails:
            existing_ids = [int(t.get("trail_id", 0)) for t in existing_trails]
            new_trail_id = max(existing_ids, default=0) + 1
        else:
            new_trail_id = 1
    except Exception as e:
        # If scan fails, start with ID 1
        new_trail_id = 1

    trail_metadata_table.put_item(Item={
        "trail_id": new_trail_id,
        "trail_name": trail
    })
    return new_trail_id

def create_device(trail_id: int) -> int:
    # Get all existing trails to find next available ID
    try:
        resp = device_metadata_table.scan()
        existing_devices = resp.get("Items", [])
        if existing_devices:
            existing_ids = [int(d.get("device_id", 0)) for d in existing_devices if str(d.get("device_id", "")).isdigit()]
            new_device_id = str(max(existing_ids, default=0) + 1)
        else:
            new_device_id = "1"
    except Exception as e:
        # If scan fails, start with ID 1
        new_device_id = "1"

    device_metadata_table.put_item(Item={
        "device_id": new_device_id,
        "current_trail_id": trail_id,
        "battery": 100
    })
    return new_device_id

def update_device(device_id: int, battery: int, last_update: int) -> None:
    device_metadata_table.update_item(
        Key={"device_id": device_id},
        UpdateExpression="SET battery=:b, last_update=:u",
        ExpressionAttributeValues={":b": battery, ":u": last_update}
    )

def add_log(trail_id: int, device_id: int, battery: int, timestamp: int):
    logs_table.put_item(Item={
        "trail_id": trail_id,
        "device_id": device_id,
        "battery": battery,
        "timestamp": timestamp
    })