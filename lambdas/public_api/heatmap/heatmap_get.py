import json
import math
from datetime import datetime, timedelta
from decimal import Decimal
from zoneinfo import ZoneInfo

from boto3.dynamodb.conditions import Key

from helper_functions import device_trail_log_day_table, device_trail_table, convert_decimals, cors_headers

algorithms = ("absolute", "relative")

def get_heatmap_data(event, context):
    try:
        print(event)
        single_params = event.get("queryStringParameters", {}) or {}
        multi_params = event.get("multiValueQueryStringParameters", {}) or {}

        trail_id_list = multi_params.get('trail_id')
        start_time = single_params.get("start_time")
        end_time = single_params.get("end_time")
        algorithm = single_params.get("algorithm", "absolute")

        if trail_id_list is None: raise ValueError("Missing required field(s): trail_id")
        if not all(id.isdigit() for id in trail_id_list): raise ValueError("Invalid trail_id_list format")
        trail_id_list_decimals = [Decimal(id) for id in trail_id_list]

        if not start_time: raise ValueError("Missing required field: start_time")
        if not end_time: raise ValueError("Missing required field: end_time")

        if algorithm not in algorithms: raise ValueError("Invalid algorithm format")

        print(f"Attempting to retrieve heatmap data for trails [{trail_id_list_decimals}], from [{start_time}] to [{end_time}] with algorithm [{algorithm}]")

        start_time = datetime.fromisoformat(start_time).astimezone(ZoneInfo("America/New_York"))
        end_time = datetime.fromisoformat(end_time).astimezone(ZoneInfo("America/New_York"))

        # Add a day to end_time (since we subtract 1 from the timestamp this won't add a real day's data)
        end_time = (end_time + timedelta(days=1)).replace(hour=0, minute=0, second=0, microsecond=0)

        trail_counts = retrieve_trail_data(trail_id_list_decimals, int(start_time.timestamp()), int(end_time.timestamp()))

        match algorithm:
            case "relative":
                trail_intensities = get_relative_intensities(trail_counts, trail_id_list_decimals, start_time, end_time)
            case _: #absolute
                trail_intensities = get_absolute_intensities(trail_counts, trail_id_list_decimals, start_time, end_time)

        print(f"Heatmap data successfully retrieved")
        return {
            "statusCode": 200,
            "headers": cors_headers(),
            "body": json.dumps(trail_intensities)
        }
    except ValueError as e:
        print(e)
        return {
            "statusCode": 400,
            "headers": cors_headers(),
            "body": json.dumps({"error": str(e)})
        }
    except Exception as e:
        print(e)
        return {
            "statusCode": 500,
            "headers": cors_headers(),
            "body": json.dumps({"error": f"Internal server error: {str(e)}"})
        }

def retrieve_trail_data(trail_id_list_decimals, start_timestamp, end_timestamp):
    device_trail_ids = []
    device_trail_cache = {}

    # get all relevant devicetrail ids from trail ids
    rows = []
    for trail_id in trail_id_list_decimals:
        rows.extend(device_trail_table.query(
            IndexName="trail-index",
            KeyConditionExpression=Key("trail_id").eq(trail_id)
        ).get("Items", []))

    # cache device-trail-devicetrail relations
    for row in rows:
        if "id" in row:
            device_trail_id = int(row["id"])
            device_trail_ids.append(device_trail_id)
            device_trail_cache[device_trail_id] = {
                "device_id": int(row["device_id"]) if "device_id" in row else "",
                "trail_id": int(row["trail_id"]) if "trail_id" in row else "",
            }

    # fetch relevant device logs from table in timestamp bounds
    device_log_rows = []
    for device_trail_id in device_trail_ids:
        rows = device_trail_log_day_table.query(
            KeyConditionExpression=Key("device_trail_id").eq(device_trail_id) & Key("start").between(start_timestamp, end_timestamp -1)
        ).get("Items", [])
        device_log_rows.extend(rows)

    device_log_rows = convert_decimals(device_log_rows)

    # append rows with trail/device ids from cache
    trail_counts = {int(id): None for id in trail_id_list_decimals}
    trail_counts[0] = 0
    for row in device_log_rows:
        id = device_trail_cache[row["device_trail_id"]].get("trail_id", 0)
        if not trail_counts.get(id):
            trail_counts[id] = 0
        trail_counts[id] += row.get("count", 0)

    return trail_counts

def convert_range(value, old_range_min, old_range_max, new_range_min, new_range_max):
    return new_range_min + (((value - old_range_min) * (new_range_max - new_range_min))/(old_range_max - old_range_min))

# In Development (Needs to be updated to not hardcode trail ids)
def get_relative_intensities(trail_counts, trail_id_list_decimals, start_time, end_time):
    trail_hikers = {
        1: (90, 20),
        2: (50, 12),
        3: (40, 10),
        4: (35, 9),
        5: (30, 8),
        6: (25, 6),
        7: (20, 5),
        8: (20, 7),
        9: (15, 5),
        10: (15, 8)
    }

    days = (end_time - start_time).days
    adapted_hikers = {trail: (data[0], data[1] / math.sqrt(days)) for trail, data in trail_hikers.items()}

    trail_intensities = {}

    for id in trail_id_list_decimals:
        if trail_counts[id] == None:
            trail_intensities[int(id)] = None
            continue
        average = trail_counts[id] / days
        id = int(id)
        data = adapted_hikers.get(id, (34, 9 / math.sqrt(days)))
        intensity = (average - data[0]) / data[1]
        if intensity < -2: intensity = -2
        if intensity > 2: intensity = 2
        trail_intensities[id] = convert_range(intensity, -2, 2, 0, 1)

    return trail_intensities

# In Development (Needs to be updated to use different absolute ranges)
def get_absolute_intensities(trail_counts, trail_id_list_decimals, start_time, end_time):
    trail_intensities = {}
    days = (end_time - start_time).days


    for id in trail_id_list_decimals:
        if trail_counts[id] == None:
            trail_intensities[int(id)] = None
            continue
        average = trail_counts[id] / days
        id = int(id)

        if average <= 19:
            trail_intensities[id] = max(convert_range(average, 0, 19, 0, .195), 0)
        elif average <= 34:
            trail_intensities[id] = convert_range(average, 20, 34, .205, .395)
        elif average <= 49:
            trail_intensities[id] = convert_range(average, 35, 49, .405, .595)
        elif average <= 74:
            trail_intensities[id] = convert_range(average, 50, 74, .605, .795)
        else:
            trail_intensities[id] = min(convert_range(average, 75, 95, .805, 1), 1)

    return trail_intensities