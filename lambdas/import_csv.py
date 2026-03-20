import hashlib
import os
import json
import csv
import re

import boto3
from decimal import Decimal

from botocore.exceptions import ClientError

dynamodb = boto3.resource('dynamodb')
s3_client = boto3.client('s3')

# Table references
logs_table = dynamodb.Table(os.environ.get("TRAIL_LOGS_TABLE", "local_TrailDeviceLogs"))
s3_bucket = os.environ.get("TRAIL_S3_BUCKET")


def cors_headers():
    return {
        "Access-Control-Allow-Origin": "*",
        "Access-Control-Allow-Methods": "GET,POST,PUT,DELETE,OPTIONS",
        "Access-Control-Allow-Headers": "Content-Type,Authorization"
    }


# Path in bucket for our uploaded hashes file
file_hash_repository_path = "import-hashes/uploaded_hashes.json"


def get_current_file_hashes():
    """
    Check our file for storing uploaded hashes, and return the list of hashes we've already uploaded.
    :return: A list of file hashes previously uploaded in the last 30 days(time set in the auto delete lambda)
    """
    try:
        hashJson = s3_client.get_object(Bucket=s3_bucket, Key=file_hash_repository_path)
        return json.loads(hashJson["Body"].read().decode("utf-8"))
    except ClientError as e:
        if e.response["Error"]["Code"] == "NoSuchKey":
            return []
        raise


def is_duplicate_hash(fileHash):
    """
    Quick check for if we've already uploaded this csv file recently. The data is the same, no reason to do it again.
    :param fileHash: The hash of the file to check
    :return: Boolean if we've uploaded the file or not
    """
    return fileHash in get_current_file_hashes()


def append_new_hash(fileHash):
    """
    Add file hash to our "already uploaded hashes" file and save it to the bucket.
    :param fileHash: The hash to add
    """
    hashes = get_current_file_hashes()
    hashes.append(fileHash)
    print(f"Appending file hash to hash list- {fileHash}")
    s3_client.put_object(Bucket=s3_bucket, Key=file_hash_repository_path,
                         Body=json.dumps(hashes).encode("utf-8"))


def parse_csv_and_export_data(event, context):
    """
    Take in a csv file, parse it, add it's contents to the database, and return a success or error state.
    Some data pruning functions taken from traildata.py and the previous project team(thanks yall)

    File limit is 5mb, checks if headers are correct, and if the file has been uploaded in the past 30 days, reject it.
    Expects: {"csv_file_path": path to the csv file in the s3 bucket}
    """
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
        expected_headers = ["Device Name", "Trail ID", "Battery %", "Last Update Timestamp"]

        if headers != expected_headers:
            raise ValueError(
                f"Incorrect headers provided. The correct formatting is {expected_headers} and you provided "
                f"{headers}. Ensure the csv file is formatted correctly and try again.")
        print(f"file headers match expected header set- {expected_headers}")

        prepared_items = []
        seen_timestamps = set()
        MIN_TIMESTAMP = 1735707600

        for row in csv_parser:

            # Load relevant field data
            device_id = row[0]
            trail_id = int(row[1])
            battery = Decimal(row[2])
            timestamp = int(row[3])

            # Ignore timestamps before minimum allowed time
            if timestamp < MIN_TIMESTAMP:
                continue

            # Skip duplicate timestamp from same device
            timestamp_key = (device_id, timestamp)
            if timestamp_key in seen_timestamps:
                continue
            seen_timestamps.add(timestamp_key)

            item = {"trail_id": trail_id, "timestamp": timestamp, "device_id": device_id,
                    "battery": battery}

            # Append item to list of rows to send
            prepared_items.append(item)

        # Send all data to table
        with logs_table.batch_writer() as batch:
            for item in prepared_items:
                batch.put_item(Item=item)
        print(f"writing {len(prepared_items)} to database")

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
