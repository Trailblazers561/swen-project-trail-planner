import os
import boto3
from boto3.dynamodb.conditions import Key, Attr
import random
from datetime import datetime, timedelta, timezone
from zoneinfo import ZoneInfo
from decimal import Decimal

dynamodb = boto3.resource('dynamodb')

# Table references
log_hour_table = dynamodb.Table(os.environ.get("DEVICE_TRAIL_LOG_HOUR_TABLE", "local_DeviceTrailLogHour"))
log_day_table = dynamodb.Table(os.environ.get("DEVICE_TRAIL_LOG_DAY_TABLE", "local_DeviceTrailLogDay"))
log_week_table = dynamodb.Table(os.environ.get("DEVICE_TRAIL_LOG_WEEK_TABLE", "local_DeviceTrailLogWeek"))
log_month_table = dynamodb.Table(os.environ.get("DEVICE_TRAIL_LOG_MONTH_TABLE", "local_DeviceTrailLogMonth"))
trail_table = dynamodb.Table(os.environ.get("TRAIL_TABLE", "local_Trail"))
device_table = dynamodb.Table(os.environ.get("DEVICE_TABLE", "local_Device"))
device_trail_table = dynamodb.Table(os.environ.get("DEVICE_TRAIL_TABLE", "local_DeviceTrail"))

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
hour_modifier = [m / 24 for m in [0.23, 0.18, 0.12, 0.12, 0.18, 0.47, 0.94, 1.40, 1.64, 1.40, 1.29, 1.17, 1.05, 1.05, 1.17, 1.40, 1.76, 2.11, 1.87, 1.52, 1.17, 0.82, 0.59, 0.35, 0.28]]

seconds_in_day = 24 * 60 * 60

def simulate_data(event, context):
    print(event)
    # Retrieve Timestamp for start of day (EST) when lambda was called
    date = datetime.fromisoformat(event["time"][:10]).replace(tzinfo=ZoneInfo("America/New_York"))
    timestamp = int(date.timestamp())

    trail_list = trail_table.scan(FilterExpression=Attr("name").is_in(list(trails.keys())))["Items"]

    for trail, stats in trails.items():
        print(f"Attempting to simulate data for trail [{trail}]")
        # Check if trail is in the database, create it if not found
        trail_exists = next((t for t in trail_list if t["name"] == trail), None)
        trail_id = trail_exists["id"] if trail_exists else create_trail(trail)

        # Check if device for the trail is in the database, create it if not
        device_trail_exists = device_trail_table.query(
            IndexName="trail-index",
            KeyConditionExpression=Key("trail_id").eq(trail_id)
        )["Items"]
        device_trail_id = device_trail_exists[0]["id"] if device_trail_exists else create_device_trail(trail_id)

        response = log_day_table.query(
            KeyConditionExpression=(
                Key("device_trail_id").eq(device_trail_id) &
                Key("start").eq(int((date - timedelta(days=1)).timestamp()))
            )
        )
        battery = response["Items"][0]["battery"] if response["Count"] >= 1 else 100

        # 1/3 chance to decrement battery
        if (battery > 1 and random.random() < 1/3):
            battery = battery - 1

        # Determine amount of hikers for the day
        hikers = max(int(random.normalvariate(*stats) * weekday_modifier[date.weekday()]), 0)
        today_start_utc = date.astimezone(timezone.utc)
        tomorrow_start_utc = (date + timedelta(days=1)).astimezone(timezone.utc)
        today_hours = int((tomorrow_start_utc - today_start_utc).total_seconds() / 3600)

        counts  = [int(hikers * m) + (random.random() < (hikers * m % 1)) for m in hour_modifier[:today_hours]]
        hikers = sum(counts)

        hour_timestamp = timestamp
        for count in counts:
            log_hour(device_trail_id, hour_timestamp, count)
            hour_timestamp += 60 * 60

        log_day(device_trail_id, timestamp, hikers, battery)

        week_timestamp = int((date - timedelta(days=(date.weekday() + 1) % 7)).timestamp())
        log_week(device_trail_id, week_timestamp, hikers, battery)

        month_timestamp = int((date.replace(day=1)).timestamp())
        log_month(device_trail_id, month_timestamp, hikers, battery)

def create_trail(trail: str) -> int:
    print(f"Creating trail with name [{trail}]")
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
        # If scan fails, start with ID 1
        new_trail_id = 1

    trail_table.put_item(Item={
        "id": new_trail_id,
        "name": trail,
        "notes": "trail auto created by simulate_data"
    })
    return new_trail_id

def create_device_trail(trail_id: int) -> int:
    print(f"Creating device for trail_id [{trail_id}]")
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
        # If scan fails, start with ID 1
        new_device_id = 1

    device_table.put_item(Item={
        "id": new_device_id,
        "name": "simulator_device",
        "notes": "device auto created by simulate_data"
    })

    print(f"Creating device_trail for trail_id [{trail_id}] and device_id [{new_device_id}]")
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
        # If scan fails, start with ID 1
        new_device_trail_id = 1

    device_trail_table.put_item(Item={
        "id": new_device_trail_id,
        "device_id": new_device_id,
        "trail_id": trail_id,
        "notes": "device_trail auto created by simulate_data"
    })
    return new_device_trail_id

def log_hour(device_trail_id: int, start: int, count: int):
    print(f"Adding hour log for device_trail_id [{device_trail_id}] at start [{start}] with count [{count}]")
    log_hour_table.put_item(Item={
        "device_trail_id": device_trail_id,
        "start": start,
        "count": count
    })

def log_day(device_trail_id: int, start: int, count: int, battery: int):
    print(f"Adding day log for device_trail_id [{device_trail_id}] at start [{start}] with count [{count}] and battery [{battery}]")
    log_day_table.put_item(Item={
        "device_trail_id": device_trail_id,
        "start": start,
        "count": count,
        "battery": battery
    })

def log_week(device_trail_id: int, start: int, count: int, battery: int):
    print(f"Adding week log for device_trail_id [{device_trail_id}] at start [{start}] with count [{count}] and battery [{battery}]")
    log_week_table.update_item(
        Key={
            "device_trail_id": device_trail_id,
            "start": start
        },
        UpdateExpression="ADD #count :count SET #battery = :battery",
        ExpressionAttributeNames={
            "#count": "count",
            "#battery": "battery"
        },
        ExpressionAttributeValues={
            ":count": count,
            ":battery": battery
        },
        ReturnValues="ALL_NEW"
    )

def log_month(device_trail_id: int, start: int, count: int, battery: int):
    print(f"Adding month log for device_trail_id [{device_trail_id}] at start [{start}] with count [{count}] and battery [{battery}]")
    log_month_table.update_item(
        Key={
            "device_trail_id": device_trail_id,
            "start": start
        },
        UpdateExpression="ADD #count :count SET #battery = :battery",
        ExpressionAttributeNames={
            "#count": "count",
            "#battery": "battery"
        },
        ExpressionAttributeValues={
            ":count": count,
            ":battery": battery
        },
        ReturnValues="ALL_NEW"
    )