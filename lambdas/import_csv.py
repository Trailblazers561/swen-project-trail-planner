import os
import json
import csv
import boto3
from decimal import Decimal

dynamodb = boto3.resource('dynamodb')
s3_client = boto3.client('s3')

# Table references
logs_table = dynamodb.Table(os.environ.get("TRAIL_LOGS_TABLE", "local_TrailDeviceLogs"))
s3_bucket = os.environ.get("TRAIL_S3_BUCKET", "local-csv_bucket-13295087")


def cors_headers():
    return {
        "Access-Control-Allow-Origin": "*",
        "Access-Control-Allow-Methods": "GET,POST,PUT,DELETE,OPTIONS",
        "Access-Control-Allow-Headers": "Content-Type,Authorization"
    }


def parse_csv_and_export_data(event, context):
    """
    Take in a csv file, parse it, add it's contents to the database, and return a success or error state.
    Some data pruning functions taken from traildata.py and the previous project team(thanks yall)
    Expects: {"csv_file_path": path to the csv file in the s3 bucket}
    """
    try:
        body = json.loads(event.get("body") or "{}")

        csv_file_path = body.get("csv_file_path")  # s3 bucket file path to csv file

        if not csv_file_path:
            raise ValueError("No csv_file_path provided")

        csv_file_data = s3_client.get_object(Bucket=s3_bucket, Key=csv_file_path)
        raw_csv = csv_file_data["Body"].read().decode("utf-8")

        csv_parser = csv.reader(raw_csv.splitlines(), delimiter=",")
        next(csv_parser)  # Ditch the header

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

        return {
            "statusCode": 200,
            "headers": cors_headers(),
            "body": json.dumps({"importSuccess": True})
        }

    except ValueError as e:
        return {
            "statusCode": 400,
            "headers": cors_headers(),
            "body": json.dumps({"error": f"Invalid data format: {str(e)}"})
        }
    except Exception as e:
        return {
            "statusCode": 500,
            "headers": cors_headers(),
            "body": json.dumps({"error": f"Internal server error: {str(e)}"})
        }