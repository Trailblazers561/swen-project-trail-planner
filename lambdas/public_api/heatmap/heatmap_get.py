import calendar
import json
from datetime import datetime, timedelta
from decimal import Decimal
from zoneinfo import ZoneInfo

from boto3.dynamodb.conditions import Key

from helper_functions import device_trail_log_day_table, device_trail_table, convert_decimals, cors_headers

time_frames = {"day": 1, "week": 7, "fortnight": 14, "month": -1}

def get_heatmap_data(event, context):
    try:
        print(event)
        single_params = event.get("queryStringParameters", {}) or {}
        multi_params = event.get("multiValueQueryStringParameters", {}) or {}

        trail_id_list = multi_params.get('trail_id')
        time_frame = single_params.get("time_frame")

        if trail_id_list is None: raise ValueError("Missing required field(s): trail_id")
        if not all(id.isdigit() for id in trail_id_list): raise ValueError("Invalid trail_id_list format")
        trail_id_list_decimals = [Decimal(id) for id in trail_id_list]

        if not time_frame: raise ValueError("Missing required field: time_frame")
        if time_frame not in time_frames: raise ValueError("Invalid time_frame format")

        print(f"Attempting to retrieve heatmap data for trails [{trail_id_list_decimals}], with time frame [{time_frame}]")

        end_time = datetime.now().astimezone(ZoneInfo("America/New_York")).replace(hour=0, minute=0, second=0, microsecond=0)
        if time_frame == "month":
            if end_time.month == 1:
                year = end_time.year - 1
                month = 12
            else:
                year = end_time.year
                month = end_time.month - 1
            start_time = end_time.replace(year=year, month=month, day=max(end_time.day, calendar.monthrange(year, month)[1]))
        else:
            start_time = end_time - timedelta(days=time_frames[time_frame])

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
                KeyConditionExpression=Key("device_trail_id").eq(device_trail_id) & Key("start").between(Decimal(start_time.timestamp()), Decimal(end_time.timestamp() -1))
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

        days = (end_time - start_time).days
        trail_intensities = {}
        for id, count in trail_counts.items():
            if count == None:
                trail_intensities[id] = None
                continue
            average = count / days
            if average <= 19:
                trail_intensities[id] = -2
            elif average <= 34:
                trail_intensities[id] = -1
            elif average <= 49:
                trail_intensities[id] = 0
            elif average <= 74:
                trail_intensities[id] = 1
            else:
                trail_intensities[id] = 2

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