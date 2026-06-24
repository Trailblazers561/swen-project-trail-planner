import json
import math
import os
import random
import urllib.request
from datetime import date, datetime, timedelta, timezone
from zoneinfo import ZoneInfo

import boto3
from boto3.dynamodb.conditions import Attr, Key

dynamodb = boto3.resource('dynamodb')

# Table references
log_hour_table = dynamodb.Table(os.environ.get("DEVICE_TRAIL_LOG_HOUR_TABLE", "local_trailcount_device_trail_hour_table"))
log_day_table = dynamodb.Table(os.environ.get("DEVICE_TRAIL_LOG_DAY_TABLE", "local_trailcount_device_trail_day_table"))
log_week_table = dynamodb.Table(os.environ.get("DEVICE_TRAIL_LOG_WEEK_TABLE", "local_trailcount_device_trail_week_table"))
log_month_table = dynamodb.Table(os.environ.get("DEVICE_TRAIL_LOG_MONTH_TABLE", "local_trailcount_device_trail_month_table"))
trail_table = dynamodb.Table(os.environ.get("TRAIL_TABLE", "local_trailcount_trail_table"))
device_table = dynamodb.Table(os.environ.get("DEVICE_TABLE", "local_trailcount_device_table"))
device_trail_table = dynamodb.Table(os.environ.get("DEVICE_TRAIL_TABLE", "local_trailcount_device_trail_table"))
device_log_table = dynamodb.Table(os.environ.get("DEVICE_LOG_TABLE", "local_trailcount_device_log_table"))

# Trails to update, Name: [mean, std_dev]
trail_hikers = {
    "Mt. Marcy": (90, 20),
    "Giant Mountain": (50, 12),
    "Poke-O-Moonshine Ranger Trail": (40, 10),
    "Mt. Skylight": (35, 9),
    "Cat Mountain": (30, 8),
    "Bald Peak": (25, 6),
    "Beaver Meadow Trail": (20, 5),
    "Mt. Haystack": (20, 7),
    "Mud Lake": (15, 5),
    "Blueberry Trail": (15, 8)
}

trail_locations = {
    "Mt. Marcy": (44.11253718129244,-73.92346562443319),
    "Giant Mountain": (44.16134866063158,-73.72068652994203),
    "Poke-O-Moonshine Ranger Trail": (44.40358464109767,-73.5023778168447),
    "Mt. Skylight": (44.0994052305797,-73.93061282259401),
    "Cat Mountain": (43.568768922716494,-73.70789845375656),
    "Bald Peak": (44.159648937334154,-73.66541145322645),
    "Mt. Haystack": (44.10566991873866,-73.9004196532753),
    "Beaver Meadow Trail": (44.56934541161058,-72.69856435671466),
    "Mud Lake": (43.21206021300888,-74.22804919647487),
    "Blueberry Trail": (44.19170852844113,-74.26349195383426)
}

# Hiker Multiplier based on day of the week Monday - Sunday
weekday_modifier = {0: .8, 1: .65, 2: .50, 3: .60, 4: .90, 5: 1.95, 6: 1.6}
hour_modifier = [m / 24 for m in [0.23, 0.18, 0.12, 0.12, 0.18, 0.47, 0.94, 1.40, 1.64, 1.40, 1.29, 1.17, 1.05, 1.05, 1.17, 1.40, 1.76, 2.11, 1.87, 1.52, 1.17, 0.82, 0.59, 0.35, 0.28]]

def simulate_data(event, context):
    print(event)
    # Retrieve Timestamp for start of day (EST) when lambda was called
    today = datetime.fromisoformat(event["time"]).astimezone(ZoneInfo("America/New_York")).replace(hour=0, minute=0, second=0, microsecond=0)
    timestamp = int(today.timestamp())

    trail_list = trail_table.scan(FilterExpression=Attr("name").is_in(list(trail_hikers.keys())))["Items"]

    for trail, stats in trail_hikers.items():
        print(f"Attempting to simulate data for trail [{trail}]")
        # Check if trail is in the database, create it if not found
        trail_exists = next((t for t in trail_list if t["name"] == trail), None)
        trail_id = trail_exists["id"] if trail_exists else create_trail(trail)

        # Check if device for the trail is in the database, create it if not
        device_trail_exists = device_trail_table.query(
            IndexName="trail-index",
            KeyConditionExpression=Key("trail_id").eq(trail_id),
            ScanIndexForward=False,
            Limit=1
        )["Items"]
        device_trail_id, device_id = device_trail_exists[0]["id"], device_trail_exists[0]["device_id"] if device_trail_exists else create_device_trail(trail_id)

        response = device_log_table.query(
            KeyConditionExpression=(
                Key("device_id").eq(device_id)
            ),
            ScanIndexForward=False,
            Limit=1
        )
        battery = response["Items"][0]["battery"] if response["Count"] >= 1 else 100

        # 1/3 chance to decrement battery
        if (battery > 1 and random.random() < 1/3):
            battery = battery - 1

        # Determine amount of hikers for the day
        multiplier = weekday_modifier[today.weekday()] * get_weather_multiplier(*trail_locations[trail]) * get_holiday_multiplier(today.date())
        hikers = max(int(random.normalvariate(*stats) * multiplier), 0)
        today_start_utc = today.astimezone(timezone.utc)
        tomorrow_start_utc = (today + timedelta(days=1)).astimezone(timezone.utc)
        today_hours = int((tomorrow_start_utc - today_start_utc).total_seconds() / 3600)

        counts  = [int(hikers * m) + (random.random() < (hikers * m % 1)) for m in hour_modifier[:today_hours]]
        hikers = sum(counts)

        hour_timestamp = timestamp
        for count in counts:
            log_hour(device_trail_id, hour_timestamp, count)
            hour_timestamp += 60 * 60

        log_day(device_trail_id, timestamp, hikers)

        week_timestamp = int((today - timedelta(days=today.weekday())).timestamp())
        log_week(device_trail_id, week_timestamp, hikers)

        month_timestamp = int((today.replace(day=1)).timestamp())
        log_month(device_trail_id, month_timestamp, hikers)

        log_log(device_id, hikers, battery)

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
    return new_device_trail_id, new_device_id

def log_hour(device_trail_id: int, start: int, count: int):
    print(f"Adding hour log for device_trail_id [{device_trail_id}] at start [{start}] with count [{count}]")
    log_hour_table.put_item(Item={
        "device_trail_id": device_trail_id,
        "start": start,
        "count": count
    })

def log_day(device_trail_id: int, start: int, count: int):
    print(f"Adding day log for device_trail_id [{device_trail_id}] at start [{start}] with count [{count}]")
    log_day_table.put_item(Item={
        "device_trail_id": device_trail_id,
        "start": start,
        "count": count
    })

def log_week(device_trail_id: int, start: int, count: int):
    print(f"Adding week log for device_trail_id [{device_trail_id}] at start [{start}] with count [{count}]")
    log_week_table.update_item(
        Key={
            "device_trail_id": device_trail_id,
            "start": start
        },
        UpdateExpression="ADD #count :count",
        ExpressionAttributeNames={
            "#count": "count"
        },
        ExpressionAttributeValues={
            ":count": count
        }
    )

def log_month(device_trail_id: int, start: int, count: int):
    print(f"Adding month log for device_trail_id [{device_trail_id}] at start [{start}] with count [{count}]")
    log_month_table.update_item(
        Key={
            "device_trail_id": device_trail_id,
            "start": start
        },
        UpdateExpression="ADD #count :count",
        ExpressionAttributeNames={
            "#count": "count"
        },
        ExpressionAttributeValues={
            ":count": count
        }
    )

def log_log(device_id: int, count: int, battery: int):
    device = device_table.get_item(Key={"id": device_id}).get("Item")

    firmware = device.get("firmware_version", "")
    time = int(datetime.now().timestamp())

    ranges = {
        "rssi": [(-65, -50), (-80, -66), (-95, -81)],
        "rsrp": [(-85, -65), (-100, -86), (-115, -101)],
        "rsrq": [(-7, -3), (-11, -8), (-14, -12)]
    }
    last = get_rndm()
    rssi = random.randint(*ranges["rssi"][last])
    last = get_rndm(last)
    rsrp = random.randint(*ranges["rsrp"][last])
    last = get_rndm(last)
    rsrq = random.randint(*ranges["rsrq"][last])
    
    print(f"Adding device log for device_id [{device_id}] at time [{time}] with count [{count}], battery [{battery}], firmware [{firmware}], rssi [{rssi}], rsrp [{rsrp}], rsrq [{rsrq}]")
    device_log_table.put_item(Item={
        "device_id": device_id,
        "time": time,
        "count": count,
        "battery": battery,
        "firmware_version": firmware,
        "rssi": rssi,
        "rsrp": rsrp,
        "rsrq": rsrq
    })

def get_rndm(last: int=0):
    rndm = random.random()
    if last == 0:
        return 0 if rndm <= .6 else 1 if rndm <= .9 else 2
    if last == 1:
        return 0 if rndm <= .4 else 1 if rndm <= .8 else 2
    if last == 2:
        return 0 if rndm <= .1 else 1 if rndm <= .7 else 2
    return 0

forecast_multipliers = (("thunder", 0.3), ("snow", 0.4), ("rain", 0.6), ("showers", 0.6), ("cloud", 1.0), ("sun", 1.3), ("clear", 1.3))
def get_forecast_multiplier(forecast):
    forecast = forecast.lower()
    for forecast_multiplier in forecast_multipliers:
        if forecast_multiplier[0] in forecast:
            return forecast_multiplier[1]
    return 1.0

def get_temp_multiplier(temp):
    return round(math.e**(-.0016 * (abs(temp - 70) ** 1.6)), 2)

def get_weather_multiplier(latitude, longitude):
    try:
        url = f"https://api.weather.gov/points/{latitude},{longitude}"

        url_request = urllib.request.Request(url, headers={"User-Agent": "AWA TrailCount"})

        with urllib.request.urlopen(url_request) as response:
            url_data = json.loads(response.read())

        weather_request = urllib.request.Request(url_data["properties"]["forecast"], headers={"User-Agent": "AWA TrailCount"})

        with urllib.request.urlopen(weather_request) as response:
            weather_data = json.loads(response.read())

        forecast_multiplier = get_forecast_multiplier(weather_data["properties"]["periods"][0]["shortForecast"])
        temp_multiplier = get_temp_multiplier(weather_data["properties"]["periods"][0]["temperature"])

        return round(forecast_multiplier * temp_multiplier, 2)
    except Exception as e:
        print(f"Error retrieving weather multiplier {e}")
        return 1.0

def nth_weekday(year, month, weekday, n):
    if n == -1:
        next_month = date(year, month + 1, 1) if month != 12 else date(year + 1, 1, 1)
        last_day = next_month - timedelta(days=1)
        return last_day - timedelta(days=(last_day.weekday() - weekday) % 7)
    else:
        start_date = date(year, month, 1)
        first_weekday = start_date + timedelta(days=(weekday - start_date.weekday()) % 7)
        return first_weekday + timedelta(weeks=n-1)

def get_holiday_multiplier(today):
    holidays = [date(today.year, 1, 1), nth_weekday(today.year, 1, 0, 3), nth_weekday(today.year, 2, 0, 3), nth_weekday(today.year, 5, 0, -1), date(today.year, 6, 19), date(today.year, 7, 4), date(today.year, 7, 9), nth_weekday(today.year, 9, 0, 1), nth_weekday(today.year, 10, 0, 2), date(today.year, 10, 31), date(today.year, 11, 11), nth_weekday(today.year, 11, 0, 4), date(today.year, 12, 25)]
    closest_holiday = 365

    for holiday in holidays:
        days_from_holiday = abs((today - holiday).days)
        days_from_holiday = min(days_from_holiday, 365 - days_from_holiday)
        if days_from_holiday < closest_holiday:
            closest_holiday = days_from_holiday

    holiday_dict = {0: 2.3, 1: 2.0, 2: 1.8, 3: 1.6, 4: 1.5}
    return holiday_dict.get(closest_holiday, 1.0)