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
    s3_client, cors_headers,
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


def upload_trail_data(event, context):
    try:
        body = event.get("body", {})
        if isinstance(body, str):
            body = json.loads(body)
        trail_id_raw = body.get("trail_id")
        data = body.get("data", [])

        if trail_id_raw is None:
            raise ValueError("Missing required field: trail_id")

        if not data:
            raise ValueError("Data array cannot be empty")

        trail_id = int(trail_id_raw)

        # Build data structures for day/week/month
        daily_logs = defaultdict(lambda: {"count": 0})
        weekly_logs = defaultdict(lambda: {"count": 0})
        monthly_logs = defaultdict(lambda: {"count": 0})
        row_data: dict[tuple, dict] = {}

        # some input validation and loading data into a format we can load into table
        for idx, point in enumerate(data):
            timestamp_raw = point.get("timestamp") or point.get("ts")
            device_id = point.get("device_id") or body.get("device_id")
            count = point.get("count") or body.get("count")

            missing = []
            if timestamp_raw is None:
                missing.append("timestamp")
            if device_id is None:
                missing.append("device_id")
            if count is None:
                missing.append("count")

            if missing:
                raise ValueError(f"Missing required fields (data[{idx}]): {', '.join(missing)}")

            try:
                timestamp = int(timestamp_raw)
            except (ValueError, TypeError):
                return {
                    "statusCode": 400,
                    "headers": cors_headers(),
                    "body": json.dumps({"error": f"Invalid timestamp format (data[{idx}])"})
                }

            timestamp_key = (device_id, timestamp)
            row_data[timestamp_key] = {"count": count}

        device_trail_id_cache = {}
        for (device_id, hour_ts), data in row_data.items():
            hour_ts = timestamp_conversion(hour_ts, "hour")
            if device_id not in device_trail_id_cache:
                device_trail_id_cache[device_id] = get_device_trail_id(device_id, trail_id)[0]
            device_trail_id = device_trail_id_cache[device_id]

            current_day = (device_trail_id, timestamp_conversion(hour_ts, "day"))
            current_week = (device_trail_id, timestamp_conversion(hour_ts, "week"))
            current_month = (device_trail_id, timestamp_conversion(hour_ts, "month"))

            # populate counts on the daily/weekly/monthly levels
            daily_logs[current_day]["count"] += data["count"]
            weekly_logs[current_week]["count"] += data["count"]
            monthly_logs[current_month]["count"] += data["count"]

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
                    "count": data["count"]
                })
        print(f"writing {len(daily_logs)} to day database")

        # Send data to week table
        with device_trail_log_week_table.batch_writer() as batch:
            for (device_trail_id, week_ts), data in weekly_logs.items():
                batch.put_item(Item={
                    "device_trail_id": device_trail_id,
                    "start": week_ts,
                    "count": data["count"]
                })
        print(f"writing {len(weekly_logs)} to week database")

        # Send data to month table
        with device_trail_log_month_table.batch_writer() as batch:
            for (device_trail_id, month_ts), data in monthly_logs.items():
                batch.put_item(Item={
                    "device_trail_id": device_trail_id,
                    "start": month_ts,
                    "count": data["count"]
                })
        print(f"writing {len(monthly_logs)} to month database")

        return {
            "statusCode": 200,
            "headers": cors_headers(),
            "body": json.dumps({"message": "Trail data uploaded"})
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


