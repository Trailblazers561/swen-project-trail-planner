import os
import json
from datetime import datetime
import boto3
from boto3.dynamodb.conditions import Attr
import csv
from pathlib import Path
import hashlib
from decimal import Decimal

dynamodb = boto3.resource('dynamodb')
s3_client = boto3.client('s3')

# Table references
logs_table = dynamodb.Table(os.environ.get("TRAIL_LOGS_TABLE", "local_TrailDeviceLogs"))
trail_metadata_table = dynamodb.Table(os.environ.get("TRAIL_METADATA_TABLE", "local_TrailMetadata"))
device_metadata_table = dynamodb.Table(os.environ.get("DEVICE_METADATA_TABLE", "local_DeviceMetadata"))
trail_groups_table = dynamodb.Table(os.environ.get("TRAIL_GROUPS_TABLE", "local_TrailGroups"))
s3_bucket = os.environ.get("TRAIL_S3_BUCKET", "local-csv_bucket-13295087")

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
    """
    Creates a csv file from the given parameters and returns link to the file in a bucket.
    Dates in iso format, all payload parameters are optional
    Expects: { "trail_id_list":  list[int], "start_date": str, "end_date": str}
    """
    try:
        body = json.loads(event.get("body") or "{}")

        trail_id_list = body.get("trail_id_list")
        start_date = body.get("start_date")
        end_date = body.get("end_date")


        if start_date is None:
            start_date = 0
        else:
            start_date = datetime.fromisoformat(start_date).timestamp()

        if end_date is None:
            end_date = 4928325678
        else:
            end_date = datetime.fromisoformat(end_date).timestamp()

        if trail_id_list is None:
            items = logs_table.scan(
                FilterExpression=Attr("timestamp").gt(start_date) & \
                    Attr("timestamp").lt(end_date)
            ).get("Items")
        else:
            items = logs_table.scan(
                FilterExpression=Attr("timestamp").gt(start_date) & \
                    Attr("timestamp").lt(end_date) & \
                    Attr("trail_id_list").is_in(trail_id_list)
            ).get("Items")
        items = convert_decimals(items)

        key = "/tmp/trail_data_export.csv"
        file_path = Path(key)
        file_path.parent.mkdir(parents=True, exist_ok=True)

        f = open(key, "w+", newline='')
        temp_csv_file = csv.writer(f)

        # non finalized headers. update with sql database structure
        temp_csv_file.writerow(["Device Name", "Trail ID", "Battery %", "Last Update Timestamp"])
        temp_csv_file.writerows([item.values() for item in items])

        f.close()

        h = hashlib.sha3_512()
        h.update(json.dumps(items, sort_keys=True).encode('utf-8'))
        fullFilePath = h.hexdigest() + "/trail_data.csv"
        s3_client.upload_file(key, s3_bucket, fullFilePath)

        url = s3_client.generate_presigned_url('get_object',
                                                    Params={'Bucket': s3_bucket,
                                                            'Key': fullFilePath},
                                                    ExpiresIn=3600)

        return {
            "statusCode": 200,
            "headers": cors_headers(),
            "body": json.dumps({"url": url})
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

def cors_headers():
    return {
        "Access-Control-Allow-Origin": "*",
        "Access-Control-Allow-Methods": "GET,POST,PUT,DELETE,OPTIONS",
        "Access-Control-Allow-Headers": "Content-Type,Authorization"
    }
#start_date="2025-05-28"&end_date="2025-15-28"&trail_id_list=[1]