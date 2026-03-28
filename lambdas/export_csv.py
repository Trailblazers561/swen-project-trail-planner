import os
import json
from datetime import datetime
import boto3
from boto3.dynamodb.conditions import Attr, Key
import csv
from pathlib import Path
import hashlib
from decimal import Decimal

dynamodb = boto3.resource('dynamodb')
s3_client = boto3.client('s3')

# Table references
device_trail_log_hour_table = dynamodb.Table(os.environ.get("DEVICE_TRAIL_LOG_HOUR_TABLE"))
device_trail_log_day_table = dynamodb.Table(os.environ.get("DEVICE_TRAIL_LOG_DAY_TABLE"))
device_trail_log_week_table = dynamodb.Table(os.environ.get("DEVICE_TRAIL_LOG_WEEK_TABLE"))
device_trail_log_month_table = dynamodb.Table(os.environ.get("DEVICE_TRAIL_LOG_MONTH_TABLE"))
trail_table = dynamodb.Table(os.environ.get("TRAIL_TABLE"))
device_table = dynamodb.Table(os.environ.get("DEVICE_TABLE"))
device_trail_table = dynamodb.Table(os.environ.get("DEVICE_TRAIL_TABLE"))
trail_group_table = dynamodb.Table(os.environ.get("TRAIL_GROUP_TABLE"))
s3_bucket = os.environ.get("TRAIL_S3_BUCKET")

table_time_map = {
    "hour":  device_trail_log_hour_table,
    "day":   device_trail_log_day_table,
    "week":  device_trail_log_week_table,
    "month": device_trail_log_month_table,
}

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
    Expects: { "trail_id_list":  list[int], "start_date": str, "end_date": str}
    """
    try:
        single_params = event.get("queryStringParameters", {}) or {}
        multi_params = event.get("multiValueQueryStringParameters", {}) or {}

        trail_id_list = multi_params.get("trail_id_list")
        start_date = single_params.get("start_date")
        end_date = single_params.get("end_date")
        granularity = single_params.get("granularity", "day").lower() # defaulting to day if not specified, prolly unnecessary but makes things easier

        if granularity not in table_time_map:
            raise ValueError(f"Invalid granularity of {granularity}. Make sure it is a valid option: {list(table_time_map.keys())}")
        log_table = table_time_map[granularity]

        if trail_id_list is not None and not all(id.isdigit() for id in trail_id_list):
            raise ValueError("Invalid trail_id_list format")
        trail_id_list_decimals = [Decimal(id) for id in trail_id_list] if trail_id_list else None

        if start_date is None:
            start_date = Decimal(0)
        else:
            start_date = Decimal(datetime.fromisoformat(start_date).timestamp())

        if end_date is None:
            end_date = Decimal(4928325678)
        else:
            end_date = Decimal(datetime.fromisoformat(end_date).timestamp())

        print(f"Attempting to export csv for trails [{trail_id_list_decimals}], from [{start_date}] to [{end_date}] at granularity of [{granularity}]")

        # take trail ids, get relevant device ids
        device_trail_ids = []
        device_trail_cache = {}

        if trail_id_list is None:
            rows = device_trail_table.scan(ProjectionExpression="id, device_id, trail_id").get("Items", [])
        else:
            rows = []
            for trail_id in trail_id_list_decimals:
                rows.extend(device_trail_table.query(
                    IndexName="trail-index",
                    KeyConditionExpression=Key("trail_id").eq(trail_id)
                ).get("Items", []))

        for row in rows:
            if "id" in row:
                dt_id = int(row["id"])
                device_trail_ids.append(dt_id)
                device_trail_cache[dt_id] = {
                    "device_id": int(row["device_id"]) if "device_id" in row else "",
                    "trail_id": int(row["trail_id"]) if "trail_id" in row else "",
                }
        if not device_trail_ids:
            raise ValueError(f"No trails found for [{trail_id_list_decimals}]")

        # take device ids, read all data from the relevant table over the date range
        trail_log_rows = []
        for device_trail_id in device_trail_ids:
            rows = log_table.query(KeyConditionExpression=Key("device_trail_id").eq(device_trail_id) &
                                   Key("start").between(start_date, end_date)).get("Items", [])
            trail_log_rows.extend(rows)
        trail_log_rows = convert_decimals(trail_log_rows)
        print(f"Found {len(trail_log_rows)} entries")

        for row in trail_log_rows:
            dt_id = row["device_trail_id"]
            row["device_id"] = device_trail_cache[dt_id].get("device_id", "")
            row["trail_id"] = device_trail_cache[dt_id].get("trail_id", "")

        # brute forcing battery on an hourly basis
        if granularity == "hour":
            cached_battery_values = {}
            for row in trail_log_rows:
                start_timestamp = row["start"]
                start_of_day = int(datetime.fromtimestamp(float(start_timestamp)).replace(hour=0, minute=0, second=0, microsecond=0).timestamp())
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

        headers = ["Device ID", "Trail ID", "Count", "Start Timestamp", "Battery %"]
        temp_csv_file.writerow(headers)

        for row in trail_log_rows:
            entry = [
                row.get("device_id"),
                row.get("trail_id", ""),
                row.get("count", ""),
                row.get("start", ""),
                row.get("battery", ""),
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
