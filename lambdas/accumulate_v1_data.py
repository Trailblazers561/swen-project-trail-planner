import json
from collections import defaultdict
from datetime import datetime, timedelta, timezone

from boto3.dynamodb.conditions import Key

from helper.helper_functions import (
    device_table,
    device_trail_table,
    device_trail_log_hour_table,
    device_trail_log_day_table,
    device_trail_log_week_table,
    device_trail_log_month_table,
    device_log_table,
    get_device_trail_id,
    timestamp_conversion,
    is_device_blocked,
    is_device_archived,
    v1_device_bucket,
    s3_client, cors_headers, upload_trail_data,
)

BUFFER_PREFIX = "buffer/"


def delete_objects(rows):
    """
    Delete entries in our s3 bucket, for the actual cleanup
    :param rows: The entries of the specific rows to delete
    """
    for i in range(0, len(rows), 1000):
        chunk = rows[i:i + 1000]
        s3_client.delete_objects(
            Bucket=v1_device_bucket,
            Delete={"Objects": [{"Key": o["Key"]} for o in chunk]},
        )


def accumulate(event, context):
    """
    Manual accumulation for the legacy v1 device data packets into a single data packet in the v2 style, performed
    at the end of the day.
    Takes the v1 data stored in an s3 bucket and creates a single fresh v2 packet from it manually, then clears the
    bucket.
    Uploads the v2 formatted data to the database, which just thinks this is a normal device.
    """
    try:
        device_entries = []
        paginator = s3_client.get_paginator('list_objects_v2')

        for page in paginator.paginate(Bucket=v1_device_bucket, Prefix=BUFFER_PREFIX):
            device_entries.extend(page.get('Contents', []))

        if not device_entries:
            return {"message": "No data to accumulate present"}

        device_entries.sort(key=lambda x: x['LastModified'])

        first_record = json.loads(
            s3_client.get_object(Bucket=v1_device_bucket, Key=device_entries[0]["Key"])["Body"].read())
        device_name = first_record.get("device_name")

        if not device_name:
            return {"message": "First data entry missing device name", "key": device_entries[0]["Key"]}

        if is_device_blocked(device_name=device_name) or is_device_archived(device_name=device_name):
            delete_objects(device_entries)
            return {"message": "Device blocked or archived, ignoring data"}

        device_exists = device_table.query(
            IndexName="name-index",
            KeyConditionExpression=Key("name").eq(device_name),
            Limit=1
        )["Items"]
        device_id = device_exists[0]["id"] if device_exists else None
        if not device_id: raise ValueError(
            f"Cannot find device with name [{device_name}], please MANUALLY register device")

        all_hikers = []
        latest_entry = {}
        for entry in device_entries:
            record = json.loads(s3_client.get_object(Bucket=v1_device_bucket, Key=entry["Key"])["Body"].read())
            all_hikers.extend(record.get("hits", []))
            latest_entry = record

        device_log_table.put_item(Item={
            "device_id": device_id,
            "time": int(datetime.now(timezone.utc).timestamp()),
            "log_type": "data_upload",
            "count": len(all_hikers),
            "battery": latest_entry.get("battery"),
            "firmware_version": latest_entry.get("firmware_version"),
            "rssi": latest_entry.get("rssi"),
            "rsrp": latest_entry.get("rsrp"),
            "rsrq": latest_entry.get("rsrq"),
            "supply_mv": latest_entry.get("supply_mv"),
        })

        if not all_hikers:
            delete_objects(device_entries)
            return {"message": "Data contains no actual hikers, dropping"}

        device_trail_results = device_trail_table.query(
            KeyConditionExpression=Key("device_id").eq(device_id),
            ScanIndexForward=False,
            Limit=1
        ).get("Items", [])

        if not device_trail_results or "date_retired" in device_trail_results[0]:
            delete_objects(device_entries)
            return {"message": "Device data logged, but must be associated to a trail to log data"}

        if "date_installed" not in device_trail_results[0]:
            delete_objects(device_entries)
            return {"message": "Device data logged, but must be marked as installed to log data"}

        trail_id = device_trail_results[0]["trail_id"]
        data_points = [{"ts": ts, "count": 1} for ts in all_hikers]

        if data_points:
            new_body = {
                "trail_id": trail_id,
                "device_id": device_id,
                "battery": latest_entry.get("battery"),
                "data": data_points
            }
            new_event = {**event, "body": new_body}

            upload_trail_data_call = upload_trail_data(new_event, context)

            if upload_trail_data_call.get("statusCode") != 200:
                error = upload_trail_data_call.get("body", "{}")
                if isinstance(error, str):
                    error = json.loads(error)
                delete_objects(device_entries)
                return {"message": "Trail data upload of accumulated data failed",
                        "error": error.get("error", "unknown error")}

        delete_objects(device_entries)

        return {"message": f"Device data logged successfully, logged {len(data_points)} hikers"}
    except Exception as e:
        print(e)
        return {"message": f"Internal server error: {str(e)}"}
