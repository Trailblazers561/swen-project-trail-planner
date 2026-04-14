import os
import json
from datetime import datetime, timedelta
from zoneinfo import ZoneInfo
import boto3
from boto3.dynamodb.conditions import Key
import csv
from pathlib import Path
import hashlib
from decimal import Decimal

dynamodb = boto3.resource('dynamodb')
s3_client = boto3.client('s3')

# Table references
device_trail_log_hour_table = dynamodb.Table(os.environ.get("DEVICE_TRAIL_LOG_HOUR_TABLE", "local_DeviceTrailLogHour"))
device_trail_log_day_table = dynamodb.Table(os.environ.get("DEVICE_TRAIL_LOG_DAY_TABLE", "local_DeviceTrailLogDay"))
device_trail_log_week_table = dynamodb.Table(os.environ.get("DEVICE_TRAIL_LOG_WEEK_TABLE", "local_DeviceTrailLogWeek"))
device_trail_log_month_table = dynamodb.Table(os.environ.get("DEVICE_TRAIL_LOG_MONTH_TABLE", "local_DeviceTrailLogMonth"))
trail_table = dynamodb.Table(os.environ.get("TRAIL_TABLE", "local_Trail"))
device_table = dynamodb.Table(os.environ.get("DEVICE_TABLE", "local_Device"))
device_trail_table = dynamodb.Table(os.environ.get("DEVICE_TRAIL_TABLE", "local_DeviceTrail"))
trail_group_table = dynamodb.Table(os.environ.get("TRAIL_GROUP_TABLE", "local_TrailGroup"))
s3_bucket = os.environ.get("TRAIL_S3_BUCKET")

table_time_map = {
    "hour":  device_trail_log_hour_table,
    "day":   device_trail_log_day_table,
    "week":  device_trail_log_week_table,
    "month": device_trail_log_month_table,
    "year": device_trail_log_month_table
}

fancy_granularity = {"hour": "Hourly", "day": "Daily", "week": "Weekly", "month": "Monthly", "year": "Yearly"}

def convert_decimals(obj):
    if isinstance(obj, list):
        return [convert_decimals(i) for i in obj]
    elif isinstance(obj, dict):
        return {k: convert_decimals(v) for k, v in obj.items()}
    elif isinstance(obj, Decimal):
        return float(obj) if obj % 1 > 0 else int(obj)
    else:
        return obj


def create_and_fill_csv(event, context):
    print(event)
    """
    Creates a csv file from the given parameters and returns link to the file in a bucket.
    Dates in iso format, all payload parameters are optional
    Expects: { "trail_id_list":  list[int], "start_date": str, "end_date": str, "granularity": str (optional)}
    """
    try:
        single_params = event.get("queryStringParameters", {}) or {}
        multi_params = event.get("multiValueQueryStringParameters", {}) or {}

        trail_id_list = multi_params.get("trail_id")
        start_date = single_params.get("start_date", "")[:10]
        end_date = single_params.get("end_date", "")[:10]
        granularity = single_params.get("granularity", "day").lower() # defaulting to day if not specified, prolly unnecessary but makes things easier

        if trail_id_list is None: raise ValueError("Missing required field(s): trail_id")
        if not all(id.isdigit() for id in trail_id_list): raise ValueError("Invalid trail_id_list format")
        trail_id_list_decimals = [Decimal(id) for id in trail_id_list]

        if not start_date: raise ValueError("Missing required field: start_date")
        start_date = Decimal(datetime.fromisoformat(start_date).replace(tzinfo=ZoneInfo("America/New_York")).timestamp())

        if not end_date: raise ValueError("Missing required field: end_date")
        if granularity == "year":
            end_date = Decimal(datetime.fromisoformat(end_date).replace(tzinfo=ZoneInfo("America/New_York"), month=12, day=31).timestamp())
        else:
            end_date = Decimal((datetime.fromisoformat(end_date).replace(tzinfo=ZoneInfo("America/New_York")) + timedelta(days=1) - timedelta(minutes=1)).timestamp())

        if granularity not in table_time_map:
            raise ValueError(f"Invalid granularity of {granularity}. Make sure it is a valid option: {list(table_time_map.keys())}")
        log_table = table_time_map[granularity]

        print(f"Attempting to export csv for trails [{trail_id_list_decimals}], from [{start_date}] to [{end_date}] at granularity of [{granularity}]")

        # take trail ids, get relevant device trail ids
        device_trail_ids = []
        device_trail_cache = {}

        device_trail_rows = []
        for trail_id in trail_id_list_decimals:
            device_trail_rows.extend(device_trail_table.query(
                IndexName="trail-index",
                KeyConditionExpression=Key("trail_id").eq(trail_id)
            ).get("Items", []))

        for row in device_trail_rows:
            if "id" in row:
                dt_id = int(row["id"])
                device_trail_ids.append(dt_id)
                device_trail_cache[dt_id] = {
                    # "device_id": int(row["device_id"]) if "device_id" in row else "", # Commented out because Craig doesn't want it
                    "trail_id": int(row["trail_id"]) if "trail_id" in row else "",
                }
        if not device_trail_ids:
            raise ValueError(f"No trails found for [{trail_id_list_decimals}]")

        trail_rows = []
        # split batch by 100 (that is the cap for keys in a batch)
        for hundred in (trail_id_list_decimals[i:i+100] for i in range(0, len(trail_id_list_decimals), 100)):
            response = dynamodb.batch_get_item(
                RequestItems={
                    trail_table.name: {"Keys": [{"id": id} for id in hundred]}
                }
            )["Responses"].get(trail_table.name, [])
            trail_rows.extend(response)
        trail_id_to_name = {0: ""}
        for row in trail_rows:
            trail_id_to_name[row.get("id", 0)] = row.get("name", "")

        # take device ids, read all data from the relevant table over the date range
        trail_log_rows = []
        for device_trail_id in device_trail_ids:
            rows = log_table.query(KeyConditionExpression=Key("device_trail_id").eq(device_trail_id) &
                                   Key("start").between(start_date, end_date)).get("Items", [])
            if granularity == "year" and rows:
                year_rows = []
                last_year = int(datetime.fromtimestamp(int(rows[0]["start"])).astimezone(ZoneInfo("America/New_York")).replace(month=1).timestamp())
                current_year_log = {"device_trail_id": device_trail_id, "start": last_year, "count": 0, "battery": None}
                for row in rows:
                    current_year = int(datetime.fromtimestamp(int(row["start"])).astimezone(ZoneInfo("America/New_York")).replace(month=1).timestamp())
                    if current_year == last_year:
                        current_year_log["count"] += row["count"]
                        current_year_log["battery"] = row["battery"]
                    else:
                        year_rows.append(current_year_log)
                        current_year_log = {"device_trail_id": device_trail_id, "start": current_year, "count": 0, "battery": None}
                        last_year = current_year
                year_rows.append(current_year_log)
                trail_log_rows.extend(year_rows)
            else:
                trail_log_rows.extend(rows)
        trail_log_rows = convert_decimals(trail_log_rows)
        print(f"Found {len(trail_log_rows)} entries")

        for row in trail_log_rows:
            dt_id = row["device_trail_id"]
            # row["device_id"] = device_trail_cache[dt_id].get("device_id", "") # Commented out because Craig doesn't want it
            row["trail_id"] = device_trail_cache[dt_id].get("trail_id", "")

        trail_log_rows.sort(key=lambda log: (log["trail_id"], log["start"]))

        # brute forcing battery on an hourly basis
        if granularity == "hour":
            cached_battery_values = {}
            for row in trail_log_rows:
                start_timestamp = row["start"]
                start_of_day = int(datetime.fromtimestamp(float(start_timestamp)).astimezone(ZoneInfo("America/New_York")).replace(hour=0, minute=0, second=0, microsecond=0).timestamp())
                cache_value = (row["device_trail_id"], start_of_day)
                if cache_value not in cached_battery_values:
                    day_entry = device_trail_log_day_table.get_item(Key={"device_trail_id": row["device_trail_id"], "start": Decimal(start_of_day)}).get("Item")
                    cached_battery_values[cache_value] = convert_decimals(day_entry).get("battery", "") if day_entry else ""
                row["battery"] = cached_battery_values[cache_value]

        key = "/tmp/trail_data_export.csv"
        file_path = Path(key)
        file_path.parent.mkdir(parents=True, exist_ok=True)

        f = open(key, "w+", newline='')
        temp_csv_file = csv.writer(f)

        headers = ["Trail ID", "Trail Name", "Start Time", f"{fancy_granularity[granularity]} Count", "Battery %"]
        temp_csv_file.writerow(headers)

        for row in trail_log_rows:
            if row.get("start"):
                start_datetime = datetime.fromtimestamp(row["start"]).astimezone(ZoneInfo("America/New_York"))
                if granularity == "hour":
                    start_date = start_datetime.strftime("%Y/%m/%d %I:%M %p")
                else:
                    start_date = start_datetime.strftime("%Y/%m/%d")
            else:
                start_date = ""
            entry = [
                row.get("trail_id", ""),
                trail_id_to_name[row.get("trail_id", 0) or 0],
                start_date,
                row.get("count", 0) or 0,
                row.get("battery", "") or ""
            ]
            temp_csv_file.writerow(entry)
        f.close()

        h = hashlib.sha3_512()
        h.update(json.dumps(trail_log_rows, sort_keys=True).encode('utf-8'))
        fullFilePath = h.hexdigest() + "/trail_data.csv"
        s3_client.upload_file(key, s3_bucket, fullFilePath)

        url = s3_client.generate_presigned_url('get_object',
                                               Params={'Bucket': s3_bucket,
                                                       'Key': fullFilePath},
                                               ExpiresIn=3600)
        print(f"Success: returning csv url [{url}]")
        return {
            "statusCode": 200,
            "headers": cors_headers(),
            "body": json.dumps({"url": url})
        }

    except ValueError as e:
        print(e)
        return {
            "statusCode": 400,
            "headers": cors_headers(),
            "body": json.dumps({"error": f"{str(e)}"})
        }
    except Exception as e:
        print(e)
        return {
            "statusCode": 500,
            "headers": cors_headers(),
            "body": json.dumps({"error": f"Internal server error: {str(e)}"})
        }

def cors_headers():
    return {
        "Access-Control-Allow-Origin": "*",
        "Access-Control-Allow-Methods": "GET,POST,PUT,DELETE,OPTIONS",
        "Access-Control-Allow-Headers": "Content-Type,Authorization"
    }