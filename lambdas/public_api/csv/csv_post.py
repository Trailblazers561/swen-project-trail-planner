import csv
import hashlib
import json
import re
from collections import defaultdict
from decimal import Decimal

from botocore.exceptions import ClientError

from helper_functions import csv_bucket, device_trail_log_hour_table, device_trail_log_day_table, device_trail_log_week_table, device_trail_log_month_table, s3_client, cors_headers, get_device_trail_id, timestamp_conversion

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

        pages = paginator.paginate(Bucket=csv_bucket, Prefix=file_hash_repository_path)

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
    s3_client.put_object(Bucket=csv_bucket, Key=filePath)

def parse_csv_and_export_data(event, context):
    """
    Take in a csv file, parse it, add it's contents to the database, and return a success or error state.
    Some data pruning functions taken from traildata.py and the previous project team(thanks yall)

    File limit is 5mb, checks if headers are correct, and if the file has been uploaded in the past 30 days, reject it.
    Expects: {"csv_file_path": path to the csv file in the s3 bucket}
    """
    print(event)
    try:
        body = event.get("body", {})
        if isinstance(body, str):
            body = json.loads(body)

        csv_file_path = body.get("csv_file_path")  # s3 bucket file path to csv file
        print(f"csv file path: {csv_file_path}")

        if not csv_file_path:
            raise ValueError("No csv_file_path provided")

        # quick little regex to ensure we match the tmp-upload/uuid/traildata.csv format
        if not re.match(r'^tmp-upload/[0-9a-f-]+/trail_data\.csv$', csv_file_path):
            raise ValueError(f"Invalid csv_file_path: {csv_file_path}")
        print("path is in the correct file path format")

        csv_file_data = s3_client.get_object(Bucket=csv_bucket, Key=csv_file_path)

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
                device_trail_id_cache[device_id] = get_device_trail_id(device_id)[0]
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
        for (device_id, hour_ts), data in row_data.items():
            device_trail_log_hour_table.update_item(
                Key={
                    "device_trail_id": device_trail_id,
                    "start": hour_ts
                },
                UpdateExpression="ADD #count :count",
                ExpressionAttributeNames={"#count": "count"},
                ExpressionAttributeValues={":count": data["count"]}
            )
        print(f"writing {len(row_data)} to hour database")

        # Send data to day table
        for (device_trail_id, day_ts), data in daily_logs.items():
            expression = "ADD #count :count"
            attribute_names = {"#count": "count"}
            attribute_values = {":count": data["count"]}
            if data["battery"] is not None:
                expression += " SET #battery = :battery"
                attribute_names["#battery"] = "battery"
                attribute_values[":battery"] = data["battery"]
            device_trail_log_day_table.update_item(
                Key={
                    "device_trail_id": device_trail_id,
                    "start": day_ts
                },
                UpdateExpression=expression,
                ExpressionAttributeNames=attribute_names,
                ExpressionAttributeValues=attribute_values
            )
        print(f"writing {len(daily_logs)} to day database")

        # Send data to week table
        for (device_trail_id, week_ts), data in weekly_logs.items():
            expression = "ADD #count :count"
            attribute_names = {"#count": "count"}
            attribute_values = {":count": data["count"]}
            if data["battery"] is not None:
                expression += " SET #battery = :battery"
                attribute_names["#battery"] = "battery"
                attribute_values[":battery"] = data["battery"]
            device_trail_log_week_table.update_item(
                Key={
                    "device_trail_id": device_trail_id,
                    "start": week_ts
                },
                UpdateExpression=expression,
                ExpressionAttributeNames=attribute_names,
                ExpressionAttributeValues=attribute_values
            )
        print(f"writing {len(weekly_logs)} to week database")

        # Send data to month table
        for (device_trail_id, month_ts), data in monthly_logs.items():
            expression = "ADD #count :count"
            attribute_names = {"#count": "count"}
            attribute_values = {":count": data["count"]}
            if data["battery"] is not None:
                expression += " SET #battery = :battery"
                attribute_names["#battery"] = "battery"
                attribute_values[":battery"] = data["battery"]
            device_trail_log_month_table.update_item(
                Key={
                    "device_trail_id": device_trail_id,
                    "start": month_ts
                },
                UpdateExpression=expression,
                ExpressionAttributeNames=attribute_names,
                ExpressionAttributeValues=attribute_values
            )
        print(f"writing {len(monthly_logs)} to month database")

        append_new_hash(csv_hash)

        s3_client.delete_object(Bucket=csv_bucket, Key=csv_file_path)

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