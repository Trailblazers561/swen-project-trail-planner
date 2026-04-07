import hashlib
import os
import json
import csv
import re
from collections import defaultdict
from datetime import datetime, timedelta
from zoneinfo import ZoneInfo

import boto3
from decimal import Decimal

from boto3.dynamodb.conditions import Key, Attr
from botocore.exceptions import ClientError

dynamodb = boto3.resource('dynamodb')
s3_client = boto3.client('s3')

# Table references
device_trail_log_hour_table = dynamodb.Table(os.environ.get("DEVICE_TRAIL_LOG_HOUR_TABLE", "local_DeviceTrailLogHour"))
device_trail_log_day_table = dynamodb.Table(os.environ.get("DEVICE_TRAIL_LOG_DAY_TABLE", "local_DeviceTrailLogDay"))
device_trail_log_week_table = dynamodb.Table(os.environ.get("DEVICE_TRAIL_LOG_WEEK_TABLE", "local_DeviceTrailLogWeek"))
device_trail_log_month_table = dynamodb.Table(os.environ.get("DEVICE_TRAIL_LOG_MONTH_TABLE", "local_DeviceTrailLogMonth"))
device_trail_table = dynamodb.Table(os.environ.get("DEVICE_TRAIL_TABLE", "local_DeviceTrail"))
s3_bucket = os.environ.get("TRAIL_S3_BUCKET")


def cors_headers():
    return {
        "Access-Control-Allow-Origin": "*",
        "Access-Control-Allow-Methods": "GET,POST,PUT,DELETE,OPTIONS",
        "Access-Control-Allow-Headers": "Content-Type,Authorization"
    }


# Path in bucket for our uploaded hashes file
file_hash_repository_path = "import-hashes/"


def is_duplicate_hash(fileHash):
    """
    Grab all files in the import-hashes folder, compare file hash to the names of the files in there to check if the file
    has been hashed.
    :param fileHash: The hash of the file to check
    :return: Boolean if we've uploaded the file or not
    """

    try:
        paginator = s3_client.get_paginator("list_objects_v2")

        pages = paginator.paginate(Bucket=s3_bucket, Prefix=file_hash_repository_path)

        hashes = []
        for page in pages:
            if 'Contents' in page:
                for obj in page['Contents']:
                    hashes.append(str(obj['Key']).removeprefix(file_hash_repository_path).removesuffix(".json"))

    except ClientError as e:
        if e.response["Error"]["Code"] == "NoSuchKey":
            return False
        raise

    return fileHash in hashes


def append_new_hash(fileHash):
    """
    Add empty json file with the file hash as the name to our bucket
    :param fileHash: The hash to add
    """
    print(f"Appending file hash to hash list- {fileHash}")
    filePath = file_hash_repository_path + fileHash + ".json"
    s3_client.put_object(Bucket=s3_bucket, Key=filePath)


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


def get_device_trail_id(device_id):
    """
    given the device id get the devicetrail id that we need for the time entries
    :param device_id: device id
    :return: devicetrail id
    """
    items = device_trail_table.query(
        KeyConditionExpression=Key("device_id").eq(device_id),
        ScanIndexForward=False,
        Limit=1
    ).get("Items", [])
    if not items:
        raise ValueError(f"No device trail association with tdevice id {device_id} found")
    return int(items[0]["id"])  # just return the id, dont need all that


def parse_csv_and_export_data(event, context):
    """
    Take in a csv file, parse it, add it's contents to the database, and return a success or error state.
    Some data pruning functions taken from traildata.py and the previous project team(thanks yall)

    File limit is 5mb, checks if headers are correct, and if the file has been uploaded in the past 30 days, reject it.
    Expects: {"csv_file_path": path to the csv file in the s3 bucket}
    """
    print(event)
    try:
        body = json.loads(event.get("body") or "{}")

        csv_file_path = body.get("csv_file_path")  # s3 bucket file path to csv file
        print(f"csv file path: {csv_file_path}")

        if not csv_file_path:
            raise ValueError("No csv_file_path provided")

        # quick little regex to ensure we match the tmp-upload/uuid/traildata.csv format
        if not re.match(r'^tmp-upload/[0-9a-f-]+/trail_data\.csv$', csv_file_path):
            raise ValueError(f"Invalid csv_file_path: {csv_file_path}")
        print("path is in the correct file path format")

        csv_file_data = s3_client.get_object(Bucket=s3_bucket, Key=csv_file_path)

        file_size_limit = 5 * 1024 * 1024  # 5 megabytes, terminate if file is too big
        if csv_file_data["ContentLength"] > file_size_limit:
            raise ValueError("File is too large, please try again with a smaller csv file")
        print("csv file is small enough to parse")

        raw_csv = csv_file_data["Body"].read().decode("utf-8")

        csv_hash = hashlib.sha256(raw_csv.encode("utf-8")).hexdigest()
        if is_duplicate_hash(csv_hash):
            raise ValueError("This file has already been uploaded")
        print("file is unique, clear to upload")

        csv_parser = csv.reader(raw_csv.splitlines(), delimiter=",")
        headers = next(csv_parser)  # Ditch the header but capture it to check
        expected_headers_alt = ["Device ID", "Count", "Start Timestamp", "Battery %", "Trail ID"]
        expected_headers = ["Device ID", "Count", "Start Timestamp",
                            "Battery %"]  # trail id is optional, both should be accepted

        if headers != expected_headers and headers != expected_headers_alt:
            raise ValueError(
                f"Incorrect headers provided. The correct formatting is {expected_headers} or {expected_headers_alt} and you provided "
                f"{headers}. Ensure the csv file is formatted correctly and try again.")

        print(f"file headers match expected header set")

        MIN_TIMESTAMP = 1735707600
        row_data: dict[tuple, dict] = {}

        for row in csv_parser:

            # Load relevant field data
            device_id = int(row[0])
            count = int(row[1])
            start_timestamp = int(row[2])
            battery = Decimal(row[3])

            # Ignore timestamps before minimum allowed time
            if start_timestamp < MIN_TIMESTAMP:
                continue

            # Skip duplicate timestamp from same device
            timestamp_key = (device_id, start_timestamp)
            row_data[timestamp_key] = {"count": count, "battery": battery}

        print(f"parsed {len(row_data)} unique hourly entries")

        # Build data structures for day/week/month
        daily_logs = defaultdict(lambda: {"count": 0, "latest_timestamp": 0, "battery": None})
        weekly_logs = defaultdict(lambda: {"count": 0, "latest_timestamp": 0, "battery": None})
        monthly_logs = defaultdict(lambda: {"count": 0, "latest_timestamp": 0, "battery": None})

        device_trail_id_cache = {}
        for (device_id, hour_ts), data in row_data.items():
            hour_ts = timestamp_conversion(hour_ts, "hour")
            if device_id not in device_trail_id_cache:
                device_trail_id_cache[device_id] = get_device_trail_id(device_id)
            device_trail_id = device_trail_id_cache[device_id]

            current_day = (device_trail_id, timestamp_conversion(hour_ts, "day"))
            current_week = (device_trail_id, timestamp_conversion(hour_ts, "week"))
            current_month = (device_trail_id, timestamp_conversion(hour_ts, "month"))

            # populate counts/battery %s on the daily/weekly/monthly levels
            daily_logs[current_day]["count"] += data["count"]
            if hour_ts > daily_logs[current_day]["latest_timestamp"] and data["battery"] is not None:
                daily_logs[current_day]["battery"] = data["battery"]
                daily_logs[current_day]["latest_timestamp"] = hour_ts

            weekly_logs[current_week]["count"] += data["count"]
            if hour_ts > weekly_logs[current_week]["latest_timestamp"] and data["battery"] is not None:
                weekly_logs[current_week]["battery"] = data["battery"]
                weekly_logs[current_week]["latest_timestamp"] = hour_ts

            monthly_logs[current_month]["count"] += data["count"]
            if hour_ts > monthly_logs[current_month]["latest_timestamp"] and data["battery"] is not None:
                monthly_logs[current_month]["battery"] = data["battery"]
                monthly_logs[current_month]["latest_timestamp"] = hour_ts

        # Send data to hour table
        with device_trail_log_hour_table.batch_writer() as batch:
            for (device_id, hour_ts), data in row_data.items():
                batch.put_item(Item={
                    "device_trail_id": device_trail_id_cache[device_id],
                    "start": hour_ts,
                    "count": data["count"],
                })
        print(f"writing {len(row_data)} to hour database")

        # Send data to day table
        with device_trail_log_day_table.batch_writer() as batch:
            for (device_trail_id, day_ts), data in daily_logs.items():
                batch.put_item(Item={
                    "device_trail_id": device_trail_id,
                    "start": day_ts,
                    "count": data["count"],
                    "battery": data["battery"] if data["battery"] is not None else ""
                })
        print(f"writing {len(daily_logs)} to day database")

        # Send data to week table
        with device_trail_log_week_table.batch_writer() as batch:
            for (device_trail_id, week_ts), data in weekly_logs.items():
                batch.put_item(Item={
                    "device_trail_id": device_trail_id,
                    "start": week_ts,
                    "count": data["count"],
                    "battery": data["battery"] if data["battery"] is not None else ""
                })
        print(f"writing {len(weekly_logs)} to week database")

        # Send data to month table
        with device_trail_log_month_table.batch_writer() as batch:
            for (device_trail_id, month_ts), data in monthly_logs.items():
                batch.put_item(Item={
                    "device_trail_id": device_trail_id,
                    "start": month_ts,
                    "count": data["count"],
                    "battery": data["battery"] if data["battery"] is not None else ""
                })
        print(f"writing {len(monthly_logs)} to month database")

        append_new_hash(csv_hash)

        s3_client.delete_object(Bucket=s3_bucket, Key=csv_file_path)

        return {
            "statusCode": 200,
            "headers": cors_headers(),
            "body": json.dumps({"importSuccess": True})
        }

    except ValueError as e:
        return {
            "statusCode": 400,
            "headers": cors_headers(),
            "body": json.dumps({"error": f"Invalid data format: {str(e)}", "importSuccess": False})
        }
    except Exception as e:
        return {
            "statusCode": 500,
            "headers": cors_headers(),
            "body": json.dumps({"error": f"Internal server error: {str(e)}", "importSuccess": False})
        }