import os
import json
import time
from collections import defaultdict
from datetime import datetime, timedelta
from zoneinfo import ZoneInfo

import boto3
from boto3.dynamodb.conditions import Key, Attr
from decimal import Decimal

dynamodb = boto3.resource('dynamodb')

# Table references
device_trail_log_hour_table = dynamodb.Table(os.environ.get("DEVICE_TRAIL_LOG_HOUR_TABLE", "local_DeviceTrailLogHour"))
device_trail_log_day_table = dynamodb.Table(os.environ.get("DEVICE_TRAIL_LOG_DAY_TABLE", "local_DeviceTrailLogDay"))
device_trail_log_week_table = dynamodb.Table(os.environ.get("DEVICE_TRAIL_LOG_WEEK_TABLE", "local_DeviceTrailLogWeek"))
device_trail_log_month_table = dynamodb.Table(os.environ.get("DEVICE_TRAIL_LOG_MONTH_TABLE", "local_DeviceTrailLogMonth"))
trail_table = dynamodb.Table(os.environ.get("TRAIL_TABLE", "local_Trail"))
device_table = dynamodb.Table(os.environ.get("DEVICE_TABLE", "local_Device"))
device_trail_table = dynamodb.Table(os.environ.get("DEVICE_TRAIL_TABLE", "local_DeviceTrail"))
trail_group_table = dynamodb.Table(os.environ.get("TRAIL_GROUP_TABLE", "local_TrailGroup"))


def convert_decimals(obj):
    if isinstance(obj, list):
        return [convert_decimals(i) for i in obj]
    elif isinstance(obj, dict):
        return {k: convert_decimals(v) for k, v in obj.items()}
    elif isinstance(obj, Decimal):
        return float(obj) if obj % 1 > 0 else int(obj)
    else:
        return obj


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
        sunday = dt_timestamp - timedelta(days=(dt_timestamp.weekday() + 1) % 7)
        return int(sunday.replace(hour=0, minute=0, second=0, microsecond=0).timestamp())
    elif time_increment == "month":
        return int(dt_timestamp.replace(day=1, hour=0, minute=0, second=0, microsecond=0).timestamp())
    return None

def get_device_trail_id(device_id, trail_id=None):
    """
    given the device id get the devicetrail id that we need for the time entries
    :param device_id: device id
    :param trail_id: trail id, optional but useful to prevent issues.
    :return: devicetrail id
    """
    if trail_id is None:
        items = device_trail_table.query(
            KeyConditionExpression=Key("device_id").eq(device_id),
            ScanIndexForward=False,
            Limit=1
        ).get("Items", [])
    else:
        items = device_trail_table.query(
            KeyConditionExpression=Key("device_id").eq(device_id),
            FilterExpression=Attr("trail_id").eq(trail_id),
            ScanIndexForward=False,
            Limit=1
        ).get("Items", [])
    if not items:
        raise ValueError(f"No device trail association with device id {device_id}, trail_id={trail_id} found")
    return int(items[0]["id"]), int(items[0]["trail_id"])  # just return the ids, dont need all that


table_time_map = {
    "hour": device_trail_log_hour_table,
    "day": device_trail_log_day_table,
    "week": device_trail_log_week_table,
    "month": device_trail_log_month_table,
}


# ========== GET TRAIL DATA ==========
def get_trail_data(event, context):
    try:
        print(event)
        single_params = event.get("queryStringParameters", {}) or {}
        multi_params = event.get("multiValueQueryStringParameters", {}) or {}

        trail_id_list = multi_params.get('trail_id')
        start = single_params.get("start")
        end = single_params.get("end")
        granularity = single_params.get("granularity", "day")

        if trail_id_list is None: raise ValueError("Missing required field(s): trail_id")
        if not all(id.isdigit() for id in trail_id_list): raise ValueError("Invalid trail_id_list format")
        trail_id_list_decimals = [Decimal(id) for id in trail_id_list]

        if not start: raise ValueError("Missing required field: start")
        if not end: raise ValueError("Missing required field: end")

        print(f"Attempting to retrieve logs for trails [{trail_id_list_decimals}], from [{start}] to [{end}] at granularity of [{granularity}]")

        if granularity not in table_time_map:
            logs_time_table = table_time_map["day"]
        else:
            logs_time_table = table_time_map[granularity]

        device_trail_ids = []
        device_trail_cache = {}

        start_time = datetime.fromisoformat(start).astimezone(ZoneInfo("America/New_York"))
        end_time = datetime.fromisoformat(end).astimezone(ZoneInfo("America/New_York"))

        # Round down start_time and round up end_time
        if granularity == "hour":
            start_time = start_time.replace(minute=0, second=0, microsecond=0)
            end_time = end_time.replace(minute=0, second=0, microsecond=0) + timedelta(hours=1)
        else:
            start_time = start_time.replace(hour=0, minute=0, second=0, microsecond=0)
            end_time = end_time.replace(hour=0, minute=0, second=0, microsecond=0) + timedelta(days=1)

        if granularity in ("week", "month"):
            partial_start_timestamp = int(start_time.timestamp())
            partial_end_timestamp = int(end_time.timestamp())
            if granularity == "week":
                query_start_timestamp = int((start_time + timedelta(days=(6 - start_time.weekday()) % 7)).timestamp())
                query_end_timestamp = int((end_time - timedelta(days=(end_time.weekday() - 6) % 7)).timestamp())
            if granularity == "month":
                query_start_timestamp = int((start_time if start_time.day == 1 else (start_time.replace(day=28) + timedelta(days=4)).replace(day=1)).timestamp())
                query_end_timestamp = int(end_time.replace(day=1).timestamp())
        else:
            query_start_timestamp = int(start_time.timestamp())
            query_end_timestamp = int(end_time.timestamp())

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
        if (query_end_timestamp > query_start_timestamp):
            for device_trail_id in device_trail_ids:
                rows = logs_time_table.query(
                    KeyConditionExpression=Key("device_trail_id").eq(device_trail_id) & Key("start").between(query_start_timestamp, query_end_timestamp -1)
                ).get("Items", [])
                device_log_rows.extend(rows)

        # Turn the extra starting days into a "partial" result
        if granularity in ("week", "month") and partial_start_timestamp < query_start_timestamp:
            start_results = device_trail_log_day_table.query(
                KeyConditionExpression=Key("device_trail_id").eq(device_trail_id) & Key("start").between(partial_start_timestamp, query_start_timestamp - 1)
            ).get("Items", [])

            if start_results:
                rows = {}
                for result in start_results:
                    if result["device_trail_id"] in rows.keys():
                        rows[result["device_trail_id"]]["count"] += result["count"]
                        rows[result["device_trail_id"]]["battery"] = result["battery"]
                    else:
                        rows[result["device_trail_id"]] = {"device_trail_id": result["device_trail_id"], "start": result["start"], "count": result["count"], "battery": result["device_trail_id"]}
                device_log_rows.extend(rows.values())

        # Turn the extra ending days into a "partial" result
        if granularity in ("week", "month") and partial_end_timestamp > query_end_timestamp:
            end_results = device_trail_log_day_table.query(
                KeyConditionExpression=Key("device_trail_id").eq(device_trail_id) & Key("start").between(query_end_timestamp, partial_end_timestamp - 1)
            ).get("Items", [])

            if end_results:
                rows = {}
                for result in end_results:
                    if result["device_trail_id"] in rows.keys():
                        rows[result["device_trail_id"]]["count"] += result["count"]
                        rows[result["device_trail_id"]]["battery"] = result["battery"]
                    else:
                        rows[result["device_trail_id"]] = {"device_trail_id": result["device_trail_id"], "start": result["start"], "count": result["count"], "battery": result["device_trail_id"]}
                device_log_rows.extend(rows.values())

        device_log_rows = convert_decimals(device_log_rows)

        # append rows with trail/device ids from cache
        for row in device_log_rows:
            device_trail_id = row["device_trail_id"]
            row["device_id"] = device_trail_cache[device_trail_id].get("device_id", "")
            row["trail_id"] = device_trail_cache[device_trail_id].get("trail_id", "")

        print(f"Logs successfully retrieved: [{device_log_rows[:3]}]")
        return {
            "statusCode": 200,
            "headers": cors_headers(),
            "body": json.dumps(device_log_rows)
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


# ========== UPLOAD TRAIL DATA ==========
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
        daily_logs = defaultdict(lambda: {"count": 0, "latest_timestamp": 0, "battery": None})
        weekly_logs = defaultdict(lambda: {"count": 0, "latest_timestamp": 0, "battery": None})
        monthly_logs = defaultdict(lambda: {"count": 0, "latest_timestamp": 0, "battery": None})
        row_data: dict[tuple, dict] = {}

        # some input validation and loading data into a format we can load into table
        for idx, point in enumerate(data):
            timestamp_raw = point.get("timestamp") or point.get("ts")
            device_id = point.get("device_id") or body.get("device_id")
            count = point.get("count") or body.get("count")
            battery = point.get("battery", body.get("battery"))

            missing = []
            if timestamp_raw is None:
                missing.append("timestamp")
            if device_id is None:
                missing.append("device_id")
            if count is None:
                missing.append("count")
            if battery is None:
                missing.append("battery")

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

            battery = Decimal(str(battery)) if isinstance(battery, float) else battery

            timestamp_key = (device_id, timestamp)
            row_data[timestamp_key] = {"count": count, "battery": battery}

        device_trail_id_cache = {}
        for (device_id, hour_ts), data in row_data.items():
            hour_ts = timestamp_conversion(hour_ts, "hour")
            if device_id not in device_trail_id_cache:
                device_trail_id_cache[device_id] = get_device_trail_id(device_id, trail_id)[0]
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

def register_device(event, context):
    """
    Handle POST requests from devices to /devices/ endpoint
    Registers a device to the database, must be called before uploading device data
    Expects: { "name": str, "firmware_version": str, "date_manufactured": str (ISO date) }
    Optional: { "notes": str}
    """
    try:
        print(event)
        body = event.get("body", {})
        if isinstance(body, str):
            body = json.loads(body)

        if not body:
            raise ValueError("Request body cannot be empty")

        name = body.get("name")
        firmware_version = body.get("firmware_version")
        date_manufactured = body.get("date_manufactured")
        notes = body.get("notes")

        if name is None: raise ValueError("Missing required field: name")
        if firmware_version is None: raise ValueError("Missing required field: firmware_version")
        if date_manufactured is None: raise ValueError("Missing required field: date_manufactured")

        date_manufactured = Decimal(datetime.fromisoformat(date_manufactured).timestamp())
        print(f"Attempting to register device with name [{name}], firmware_version [{firmware_version}], date_manufactured [{date_manufactured}], notes [{notes}]")

        id = get_next_device_id()

        item = {
            "id": id,
            "name": name,
            "firmware_version": firmware_version,
            "date_manufactured": date_manufactured
        }
        if notes:
            item["notes"] = notes
        device_table.put_item(Item=item)
        print(f"Successfully added device with id [{id}]")
        return {
            "statusCode": 200,
            "headers": cors_headers(),
            "body": json.dumps({
                "message": "Device created successfully",
                "device_id": id
            })
        }

    except ValueError as e:
        print(e)
        return {
            "statusCode": 400,
            "headers": cors_headers(),
            "body": json.dumps({"error": f"Invalid data format: {str(e)}"})
        }
    except Exception as e:
        print(e)
        return {
            "statusCode": 500,
            "headers": cors_headers(),
            "body": json.dumps({"error": f"Internal server error: {str(e)}"})
        }

# ========== UPLOAD DEVICE DATA ==========
def upload_device_data(event, context):
    """
    Handle PUT requests from devices to /devices/ endpoint.
    Supports compact payloads such as:
    {
        "name": "deviceA",
        "battery": 94,
        "data": [{"ts": 123}],
        "firmware_version": "1.2.17"
    }
    A device should be registered in the system before using this.
    """
    try:
        print(event)
        body = event.get("body","{}")
        if isinstance(body, str):
            body = json.loads(body)

        if not body:
            raise ValueError("Request body cannot be empty")

        name = body.get("name")
        if not name: raise ValueError("Missing required field: name")

        firmware_version = body.get("firmware_version")
        data_points = body.get("data")
        battery = body.get("battery")

        if not firmware_version and not (data_points and battery): raise ValueError("Missing required field: firmware_version or (data_points and battery)")

        device_exists = device_table.query(
            IndexName="name-index",
            KeyConditionExpression=Key("name").eq(name),
            Limit=1
        )["Items"]
        device_id = device_exists[0]["id"] if device_exists else None
        if not device_id: raise ValueError(f"Cannot find device with name [{name}], please register if not done already")
        messages = []

        if firmware_version:
            print(f"Attempting to update firmware version of device [{device_id}] to version [{firmware_version}]")
            device_table.update_item(
                Key={"id": device_id},
                UpdateExpression="SET firmware_version = :firmware_version",
                ExpressionAttributeValues={
                    ":firmware_version": firmware_version
                }
            )
            messages.append("Firmware version updated successfully")
            print("Successfully updated firmware version")

        if data_points and battery:
            if not isinstance(data_points, list):
                raise ValueError("Data field must be an array")

            if len(data_points) == 0:
                raise ValueError("Data array must be a non-empty list")

            print(f"Attempting to upload data of device [{device_id}] to with data [{data_points}] and battery [{battery}]")

            _, trail_id = get_device_trail_id(device_id)

            new_body = {
                "trail_id": trail_id,
                "device_id": device_id,
                "battery": battery,
                "data": data_points
            }
            new_event = {**event, "body": new_body}

            upload_trail_data_call = upload_trail_data(new_event, context)
            if upload_trail_data_call["statusCode"] == 200:
                messages.append("Device data uploaded successfully")
            else:
                return upload_trail_data_call

        return {
            "statusCode": 200,
            "headers": cors_headers(),
            "body": json.dumps({"message": ", ".join(messages)})
        }
    except ValueError as e:
        print(e)
        return {
            "statusCode": 400,
            "headers": cors_headers(),
            "body": json.dumps({"error": f"Invalid data format: {str(e)}"})
        }
    except Exception as e:
        print(e)
        return {
            "statusCode": 500,
            "headers": cors_headers(),
            "body": json.dumps({"error": f"Internal server error: {str(e)}"})
        }

# ========== METADATA ENDPOINTS ==========
def get_trail_metadata(event, context):
    try:
        print(event)
        multi_params = event.get("multiValueQueryStringParameters", {}) or {}

        trail_id_list = multi_params.get("trail_id")
        if trail_id_list is not None and not all(id.isdigit() for id in trail_id_list):
            raise ValueError("Invalid trail_id_list format")
        trail_id_list_decimals = [int(id) for id in trail_id_list] if trail_id_list else None

        print(f"Retrieving trail metadata for trail_id_list [{trail_id_list_decimals}]")
        if trail_id_list_decimals:
            items = []
            # split batch by 100 (that is the cap for keys in a batch)
            for hundred in (trail_id_list_decimals[i:i+100] for i in range(0, len(trail_id_list_decimals), 100)):
                response = dynamodb.batch_get_item(
                    RequestItems={
                        trail_table.name: {"Keys": [{"id": id} for id in hundred]}
                    }
                )["Responses"].get(trail_table.name, [])
                items.extend(response)
        else:   
            items = trail_table.scan(FilterExpression=Attr("date_retired").not_exists()).get("Items", [])

        print(f"Successfully found trail metadata [{items[:3]}]")
        return {
            "statusCode": 200,
            "headers": cors_headers(),
            "body": json.dumps(convert_decimals(items))
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

def get_device_metadata(event, context):
    try:
        print(event)
        multi_params = event.get("multiValueQueryStringParameters", {}) or {}

        device_id_list = multi_params.get("device_id")
        if device_id_list is not None and not all(id.isdigit() for id in device_id_list):
            raise ValueError("Invalid device_id_list format")
        device_id_list_decimals = [int(id) for id in device_id_list] if device_id_list else None

        print(f"Retrieving device metadata for device_id_list [{device_id_list_decimals}]")
        if device_id_list_decimals:
            items = []
            # split batch by 100 (that is the cap for keys in a batch)
            for hundred in (device_id_list_decimals[i:i+100] for i in range(0, len(device_id_list_decimals), 100)):
                response = dynamodb.batch_get_item(
                    RequestItems={
                        device_table.name: {"Keys": [{"id": id} for id in hundred]}
                    }
                )["Responses"].get(device_table.name, [])
                items.extend(response)
        else:
            items = device_table.scan().get("Items", [])

        print(f"Successfully found device metadata [{items[:3]}], attempting to append additional information")

        # Retrieve and add additional fields from DeviceTrail table information 
        desired_device_trail_fields = ["trail_id", "notes", "date_installed", "date_removed"]
        for item in items:
            device_trails_result = device_trail_table.query(
                KeyConditionExpression=Key("device_id").eq(item["id"]),
                ScanIndexForward=False
            ).get("Items", [])
            # Construct a list from the result with all params matching those from desired_device_trail_fields
            device_trails = [{field: device_trail[field] for field in desired_device_trail_fields if device_trail.get(field)} for device_trail in device_trails_result]
            item["trail_history"] = device_trails
            if len(device_trails_result):
                item["current_trail_id"] = device_trails_result[0]["trail_id"]
                day_result = device_trail_log_day_table.query(
                    KeyConditionExpression=Key("device_trail_id").eq(device_trails_result[0]["id"]),
                    ScanIndexForward=False,
                    Limit=1
                ).get("Items", [])
                if day_result:
                    item["battery"] = day_result[0]["battery"]
                    item["last_updated"] = day_result[0]["start"]

        print(f"Successfully appended device metadata [{items[:3]}]")
        return {
            "statusCode": 200,
            "headers": cors_headers(),
            "body": json.dumps(convert_decimals(items))
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

def get_trail_group_metadata(event, context):
    try:
        print(event)
        multi_params = event.get("multiValueQueryStringParameters", {}) or {}

        trail_group_list = multi_params.get("trail_group")

        print(f"Retrieving trail groups for trail_group_list [{trail_group_list}]")
        if trail_group_list:
            items = []
            # split batch by 100 (that is the cap for keys in a batch)
            for hundred in (trail_group_list[i:i+100] for i in range(0, len(trail_group_list), 100)):
                response = dynamodb.batch_get_item(
                    RequestItems={
                        trail_group_table.name: {"Keys": [{"name": name} for name in hundred]}
                    }
                )["Responses"].get(trail_group_table.name, [])
                items.extend(response)
        else:   
            items = trail_group_table.scan().get("Items", [])

        print(f"Successfully found trail groups [{items[:3]}]")
        return {
            "statusCode": 200,
            "headers": cors_headers(),
            "body": json.dumps(convert_decimals(items))
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

def create_trail(event, context):
    """
    Create a new trail. Auto-generates trail_id as next available ID.
    Expects: { "trail_name": str, "trail_group": str (optional), "notes": str (optional), "latitude": int (optional), "longitude": int (optional) }
    Returns: { "trail_id": int, "message": str }
    """
    try:
        print(event)
        body = event.get("body", {})
        if isinstance(body, str):
            body = json.loads(body)

        trail_name = body.get("trail_name")
        trail_group = body.get("trail_group")
        notes = body.get("notes")
        latitude = body.get("latitude")
        longitude = body.get("longitude")

        if not trail_name:
            return {
                "statusCode": 400,
                "headers": cors_headers(),
                "body": json.dumps({"error": "Missing required field: trail_name"})
            }

        print(f"Attempting to create trail with trail_name [{trail_name}] and trail_group [{trail_group}] and notes [{notes}] and latitude [{latitude}] and longitude [{longitude}]")

        new_trail_id = get_next_trail_id()

        # Create trail metadata
        item = {
            "id": new_trail_id,
            "name": str(trail_name)
        }

        if notes is not None:
            item["notes"] = notes
        if latitude is not None:
            item["latitude"] = Decimal(str(latitude))
        if longitude is not None:
            item["longitude"] = Decimal(str(longitude))

        try:
            trail_table.put_item(Item=item)
        except Exception as e:
            print(e)
            return {
                "statusCode": 500,
                "headers": cors_headers(),
                "body": json.dumps({"error": f"Failed to create trail: {str(e)}"})
            }

        # Always add trail to "All Areas" group
        # Then add to specified group if provided
        try:
            resp = trail_group_table.scan()
            groups = resp.get("Items", [])

            # Step 1: Add to "All Areas" group (all trails should be in this group)
            all_areas_found = False
            for group in groups:
                if group.get("name") == "All Areas":
                    trail_ids = group.get("trail_ids", [])
                    if not isinstance(trail_ids, list):
                        trail_ids = []
                    if new_trail_id not in trail_ids:
                        trail_ids.append(new_trail_id)
                    trail_group_table.put_item(Item={
                        "name": "All Areas",
                        "trail_ids": trail_ids
                    })
                    all_areas_found = True
                    break

            # If "All Areas" group doesn't exist, create it
            if not all_areas_found:
                trail_group_table.put_item(Item={
                    "name": "All Areas",
                    "trail_ids": [new_trail_id]
                })

            # Step 2: Add to specified trail group if provided (in addition to "All Areas")
            if trail_group and trail_group != "All Areas":
                group_found = False
                for group in groups:
                    if group.get("name") == trail_group:
                        trail_ids = group.get("trail_ids", [])
                        if not isinstance(trail_ids, list):
                            trail_ids = []
                        if new_trail_id not in trail_ids:
                            trail_ids.append(new_trail_id)
                        trail_group_table.put_item(Item={
                            "name": trail_group,
                            "trail_ids": trail_ids
                        })
                        group_found = True
                        break

                if not group_found:
                    trail_group_table.put_item(Item={
                        "name": trail_group,
                        "trail_ids": [new_trail_id]
                    })
        except Exception as e:
            print(f"Trail group updated failed with exception: {e}")
            # Continue even if trail group update fails
            pass

        print(f"Successfully added trail with trail_id [{new_trail_id}]")
        return {
            "statusCode": 200,
            "headers": cors_headers(),
            "body": json.dumps({
                "message": "Trail created successfully",
                "trail_id": new_trail_id
            })
        }
    except Exception as e:
        print(e)
        return {
            "statusCode": 500,
            "headers": cors_headers(),
            "body": json.dumps({"error": f"Internal server error: {str(e)}"})
        }


def update_trail_metadata(event, context):
    """
    Update trail metadata (trail name, trail group).
    Expects: { "trail_id": int, "trail_name": str, "trail_group": str, "trail_notes": str, "trail_latitude": float, "trail_longitude": float }
    """
    try:
        print(event)
        body = event.get("body", {})
        if isinstance(body, str):
            body = json.loads(body)

        trail_id = body.get("trail_id")
        trail_name = body.get("trail_name")
        trail_group = body.get("trail_group")
        trail_notes = body.get("trail_notes")
        trail_lat = body.get("trail_latitude")
        trail_lon = body.get("trail_longitude")

        if trail_id is None:
            return {
                "statusCode": 400,
                "headers": cors_headers(),
                "body": json.dumps({"error": "Missing required field: trail_id"})
            }

        print(f"Attempting to update trail with trail_id [{trail_id}] to trail_name [{trail_name}] and trail_group [{trail_group}] and notes [{trail_notes}] and latitude [{trail_lat}] and longitude [{trail_lon}]")

        try:
            trail_id = int(trail_id)
        except (ValueError, TypeError):
            return {
                "statusCode": 400,
                "headers": cors_headers(),
                "body": json.dumps({"error": "Invalid trail_id format"})
            }

        # Update trail metadata
        item = {"id": trail_id}
        if trail_name is not None:
            item["name"] = str(trail_name)
        if trail_notes is not None:
            item["notes"] = str(trail_notes)
        if trail_lat is not None:
            item["latitude"] = Decimal(str(trail_lat))
        if trail_lon is not None:
            item["longitude"] = Decimal(str(trail_lon))

        try:
            trail_table.put_item(Item=item)
        except Exception as e:
            print(e)
            return {
                "statusCode": 500,
                "headers": cors_headers(),
                "body": json.dumps({"error": f"Failed to update trail metadata: {str(e)}"})
            }

        # Update trail groups if trail_group is provided (and not empty string)
        if trail_group is not None and trail_group != "":
            try:
                # Get current trail groups
                resp = trail_group_table.scan()
                groups = resp.get("Items", [])

                # First, remove trail_id from all other groups (except "All Areas")
                # "All Areas" should always contain all trails
                for group in groups:
                    group_name = group.get("name")
                    if group_name != trail_group and group_name != "All Areas":
                        trail_ids = group.get("trail_ids", [])
                        if isinstance(trail_ids, list) and trail_id in trail_ids:
                            trail_ids = [tid for tid in trail_ids if tid != trail_id]
                            trail_group_table.put_item(Item={
                                "name": group_name,
                                "trail_ids": trail_ids
                            })

                # Ensure trail is in "All Areas" (all trails should be in this group)
                all_areas_found = False
                for group in groups:
                    if group.get("name") == "All Areas":
                        trail_ids = group.get("trail_ids", [])
                        if not isinstance(trail_ids, list):
                            trail_ids = []
                        if trail_id not in trail_ids:
                            trail_ids.append(trail_id)
                        trail_group_table.put_item(Item={
                            "name": "All Areas",
                            "trail_ids": trail_ids
                        })
                        all_areas_found = True
                        break

                # If "All Areas" doesn't exist, create it
                if not all_areas_found:
                    trail_group_table.put_item(Item={
                        "name": "All Areas",
                        "trail_ids": [trail_id]
                    })

                # Find the target group and add trail_id to it (if not "All Areas")
                if trail_group != "All Areas":
                    group_found = False
                    for group in groups:
                        if group.get("name") == trail_group:
                            trail_ids = group.get("trail_ids", [])
                            if not isinstance(trail_ids, list):
                                trail_ids = []
                            if trail_id not in trail_ids:
                                trail_ids.append(trail_id)
                            trail_group_table.put_item(Item={
                                "name": trail_group,
                                "trail_ids": trail_ids
                            })
                            group_found = True
                            break

                    # If group doesn't exist, create it
                    if not group_found:
                        trail_group_table.put_item(Item={
                            "name": trail_group,
                            "trail_ids": [trail_id]
                        })
            except Exception as e:
                print(f"Failed updating trail group with exception: {e}")
                # Continue even if trail group update fails
                pass
        else:
            # If trail_group is None (empty string), ensure trail is still in "All Areas"
            # This handles the case when removing a trail from a specific group
            try:
                resp = trail_group_table.scan()
                groups = resp.get("Items", [])

                # Remove from all groups except "All Areas"
                for group in groups:
                    group_name = group.get("name")
                    if group_name != "All Areas":
                        trail_ids = group.get("trail_ids", [])
                        if isinstance(trail_ids, list) and trail_id in trail_ids:
                            trail_ids = [tid for tid in trail_ids if tid != trail_id]
                            trail_group_table.put_item(Item={
                                "name": group_name,
                                "trail_ids": trail_ids
                            })

                # Ensure trail is in "All Areas"
                all_areas_found = False
                for group in groups:
                    if group.get("name") == "All Areas":
                        trail_ids = group.get("trail_ids", [])
                        if not isinstance(trail_ids, list):
                            trail_ids = []
                        if trail_id not in trail_ids:
                            trail_ids.append(trail_id)
                        trail_group_table.put_item(Item={
                            "name": "All Areas",
                            "trail_ids": trail_ids
                        })
                        all_areas_found = True
                        break

                # If "All Areas" doesn't exist, create it
                if not all_areas_found:
                    trail_group_table.put_item(Item={
                        "name": "All Areas",
                        "trail_ids": [trail_id]
                    })
            except Exception as e:
                print(f"Failed updating trail group with exception: {e}")
                # Continue even if trail group update fails
                pass

        print("Successfully updated trail metadata")
        return {
            "statusCode": 200,
            "headers": cors_headers(),
            "body": json.dumps({"message": "Trail metadata updated successfully"})
        }
    except Exception as e:
        print(e)
        return {
            "statusCode": 500,
            "headers": cors_headers(),
            "body": json.dumps({"error": f"Internal server error: {str(e)}"})
        }


def delete_trail(event, context):
    """
    Retires a trail and all associated data.
    Deletes:
    - Trail from all trail groups
    - Updates devices_trail date removed to given date
    - Updates trail date retired to given date
    Expects: { "trail_id": int, date: str (ISO Date, optional) }
    """
    try:
        print(event)
        body = event.get("body", {})
        if isinstance(body, str):
            body = json.loads(body)

        trail_id = body.get("trail_id")
        date = body.get("date")

        if trail_id is None:
            print("Missing required field: trial_id")
            return {
                "statusCode": 400,
                "headers": cors_headers(),
                "body": json.dumps({"error": "Missing required field: trail_id"})
            }

        try:
            trail_id = int(trail_id)
        except (ValueError, TypeError):
            print("Failed to delete trail due to invalid trail_id format")
            return {
                "statusCode": 400,
                "headers": cors_headers(),
                "body": json.dumps({"error": "Invalid trail_id format"})
            }

        if date is None:
            date = int(time.time())
        else:
            date = Decimal(datetime.fromisoformat(date).timestamp())

        print(f"Attempting to retire trail with trail_id [{trail_id}] with date [{date}]")

        # get all relevant devicetrail ids for this trail
        response = device_trail_table.query(
            IndexName="trail-index",
            KeyConditionExpression=Key("trail_id").eq(trail_id)
        )
        device_trail_items = response.get("Items", [])

        for device_trail_item in device_trail_items:
            if not device_trail_item["date_removed"]:
                device_trail_table.update_item(
                    Key={"device_id": device_trail_item["device_id"], "date_installed": device_trail_item["date_installed"]},
                    UpdateExpression="SET date_removed = :date_removed",
                    ExpressionAttributeValues={":date_removed": date}
                )

        # Remove trail from all trail groups
        try:
            resp = trail_group_table.scan()
            groups = resp.get("Items", [])

            for group in groups:
                trail_ids = group.get("trail_ids", [])
                if isinstance(trail_ids, list) and trail_id in trail_ids:
                    trail_ids = [tid for tid in trail_ids if tid != trail_id]
                    trail_group_table.put_item(Item={
                        "name": group.get("name"),
                        "trail_ids": trail_ids
                    })
        except Exception as e:
            # Log error but continue
            print(f"Error removing trail from groups: {str(e)}")

        try:
            trail_table.update_item(
                Key={"id": trail_id},
                UpdateExpression="SET date_retired = :date_retired",
                ExpressionAttributeValues={":date_retired": date}
            )
        except Exception as e:
            print(e)
            return {
                "statusCode": 500,
                "headers": cors_headers(),
                "body": json.dumps({"error": f"Failed to retire trail: {str(e)}"})
            }

        print("Successfully retired trail")
        return {
            "statusCode": 200,
            "headers": cors_headers(),
            "body": json.dumps({"message": "Trail and all associated data retired successfully"})
        }
    except Exception as e:
        print(e)
        return {
            "statusCode": 500,
            "headers": cors_headers(),
            "body": json.dumps({"error": f"Internal server error: {str(e)}"})
        }


def update_device_trail_association(event, context):
    """
    Update device trail association. Updates DeviceTrail to change which trail
    a device is associated with. Future data from this device will use the new trail_id.
    Expects: { "device_id": str, "trail_id": int }
    Optional: { "date_installed": str (ISO date), "date_removed": str (ISO date)}
    """
    try:
        print(event)
        body = event.get("body", {})
        if isinstance(body, str):
            body = json.loads(body)

        device_id = body.get("device_id")
        trail_id = body.get("trail_id")
        date_installed = body.get("date_installed")
        date_removed = body.get("date_removed")

        if device_id is None: raise ValueError("Missing required field: device_id")
        try:
            device_id = int(device_id)
        except (ValueError, TypeError):
            raise ValueError("Invalid device_id format")

        if trail_id is None: raise ValueError("Missing required field: trail_id")
        try:
            trail_id = int(trail_id)
        except (ValueError, TypeError):
            raise ValueError("Invalid trail_id format")

        if date_installed is None:
            date_installed = int(time.time())
        else:
            date_installed = Decimal(datetime.fromisoformat(date_installed).timestamp())

        if date_removed is None:
            date_removed = int(time.time())
        else:
            date_removed = Decimal(datetime.fromisoformat(date_removed).timestamp())

        print(f"Attempting to update device_trail_association with device_id [{device_id}] and trail_id [{trail_id}] and date_installed [{date_installed}] and date_removed [{date_removed}]")

        # Find current device_trail_assocation for device_id
        resp = device_trail_table.query(
            KeyConditionExpression=Key("device_id").eq(device_id)
        )
        items = resp.get("Items", [])

        old_device_trail = next((item for item in items if item.get("date_removed") is None), None)
        # If there is an existing device_trail with a different trail_id then consider it removed
        if old_device_trail and old_device_trail["trail_id"] != trail_id:
            print(f"Setting old device_trail_association [{old_device_trail['id']}] to removed ")
            device_trail_table.update_item(
                Key={"device_id": device_id, "date_installed": old_device_trail["date_installed"]},
                UpdateExpression="SET date_removed = :date_removed",
                ExpressionAttributeValues={":date_removed": date_removed}
            )

        # If we don't have a current device_trail with this device/trail combo then create a new one
        if not old_device_trail or old_device_trail["trail_id"] != trail_id:
            next_device_trail_id = get_next_device_trail_id()
            print(f"Creating new device_trail log with id [{next_device_trail_id}]")
            device_trail_table.put_item(
                Item={
                    "id": next_device_trail_id,
                    "device_id": device_id,
                    "trail_id": trail_id,
                    "date_installed": date_installed,
                }
            )

        print("Successfully updated device trail association")
        return {
            "statusCode": 200,
            "headers": cors_headers(),
            "body": json.dumps({"message": "Device trail association updated successfully"})
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

def get_next_trail_id() -> int:
    print("Retrieving next trail_id")
    # Get all existing trails to find next available ID
    try:
        resp = trail_table.scan()
        existing_trails = resp.get("Items", [])
        if existing_trails:
            existing_ids = [int(t.get("id", 0)) for t in existing_trails]
            new_trail_id = max(existing_ids, default=0) + 1
        else:
            new_trail_id = 1
    except Exception as e:
        print(f"Error finding max trail_id, starting with 1. Exception: {e}")
        # If scan fails, start with ID 1
        new_trail_id = 1

    return new_trail_id

def get_next_device_id() -> int:
    print("Retrieving next device_id")
    # Get all existing devices to find next available ID
    try:
        resp = device_table.scan()
        existing_devices = resp.get("Items", [])
        if existing_devices:
            existing_ids = [int(d.get("id", 0)) for d in existing_devices]
            new_device_id = max(existing_ids, default=0) + 1
        else:
            new_device_id = 1
    except Exception as e:
        print(f"Error finding max device_id, starting with 1. Exception: {e}")
        # If scan fails, start with ID 1
        new_device_id = 1

    return new_device_id

def get_next_device_trail_id() -> int:
    print("Retrieving next device_trail_id")
    # Get all existing device_trails to find next available ID
    try:
        resp = device_trail_table.scan()
        existing_device_trails = resp.get("Items", [])
        if existing_device_trails:
            existing_ids = [int(dt.get("id", 0)) for dt in existing_device_trails]
            new_device_trail_id = max(existing_ids, default=0) + 1
        else:
            new_device_trail_id = 1
    except Exception as e:
        print(f"Error finding max device_trail_id, starting with 1. Exception: {e}")
        # If scan fails, start with ID 1
        new_device_trail_id = 1

    return new_device_trail_id

def cors_headers():
    return {
        "Access-Control-Allow-Origin": "*",
        "Access-Control-Allow-Methods": "GET,POST,PUT,DELETE,OPTIONS",
        "Access-Control-Allow-Headers": "Content-Type,Authorization"
    }