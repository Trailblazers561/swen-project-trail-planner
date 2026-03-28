import os
import json
import time
from collections import defaultdict
from datetime import datetime, timezone

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
    dt_timestamp = datetime.fromtimestamp(timestamp, tz=timezone.utc)
    if time_increment == "day":
        return int(dt_timestamp.replace(hour=0, minute=0, second=0, microsecond=0).timestamp())
    elif time_increment == "week":
        monday = dt_timestamp - __import__('datetime').timedelta(days=dt_timestamp.weekday())
        return int(monday.replace(hour=0, minute=0, second=0, microsecond=0).timestamp())
    elif time_increment == "month":
        return int(dt_timestamp.replace(day=1, hour=0, minute=0, second=0, microsecond=0).timestamp())
    return None

def get_deviceTrail_id(device_id, trail_id=None):
    """
    given the device id get the devicetrail id that we need for the time entries
    :param device_id: device id
    :param trail_id: trail id, optional but useful to prevent issues.
    :return: devicetrail id
    """
    if trail_id is None:
        items = device_trail_table.query(
            KeyConditionExpression=Key("device_id").eq(device_id),
        ).get("Items", [])
    else:
        items = device_trail_table.query(
            KeyConditionExpression=Key("device_id").eq(device_id),
            FilterExpression=Attr("trail_id").eq(trail_id)
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
        params = event.get('queryStringParameters', {}) or {}
        trails = params.get('trails')
        start = params.get('start')
        end = params.get('end')
        granularity = params.get('granularity')

        if granularity not in table_time_map:
            logs_time_table = table_time_map["day"]
        else:
            logs_time_table = table_time_map[granularity]

        device_trail_ids = []
        device_trail_cache = {}

        start_timestamp = Decimal(0) if not start else Decimal(datetime.fromisoformat(start).timestamp())
        end_timestamp = Decimal(99999999999) if not end else Decimal(
            datetime.fromisoformat(end).timestamp())  # suitably big enough for a default

        # get all relevant devicetrail ids from trail ids
        if trails is None:
            rows = device_trail_table.scan(ProjectionExpression="id, device_id, trail_id").get("Items", [])
        else:
            rows = []
            for trail_id in [Decimal(t) for t in trails.split(',')]:
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
        for device_trail_id in device_trail_ids:
            rows = logs_time_table.query(
                KeyConditionExpression=Key("device_trail_id").eq(device_trail_id) & Key("start").between(start_timestamp,
                                                                                                         end_timestamp)
            ).get("Items", [])
            device_log_rows.extend(rows)

        device_log_rows = convert_decimals(device_log_rows)

        # append rows with trail/device ids from cache
        for row in device_log_rows:
            device_trail_id = row["device_trail_id"]
            row["device_id"] = device_trail_cache[device_trail_id].get("device_id", "")
            row["trail_id"] = device_trail_cache[device_trail_id].get("trail_id", "")

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
        body = json.loads(event.get("body", "{}"))
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
            if device_id not in device_trail_id_cache:
                device_trail_id_cache[device_id] = get_deviceTrail_id(device_id, trail_id)[0]
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


# ========== UPLOAD DEVICE DATA ==========
def upload_device_data(event, context):
    """
    Handle POST requests from devices to /devices/ endpoint.
    Supports compact payloads such as:
    {
        "device_id": "deviceA",
        "battery": 94,
        "data": [{"ts": 123}]
    }
    A device should be registered in the system before using this.
    """
    try:
        body = json.loads(event.get("body", "{}"))

        if not body:
            raise ValueError("Request body cannot be empty")

        device_id_raw = body.get("device_id")
        device_id = str(device_id_raw) if device_id_raw is not None else None
        data_points = body.get("data")
        battery = body.get("battery")

        missing_fields = []
        if not device_id:
            missing_fields.append("device_id")
        if data_points is None:
            missing_fields.append("data")

        if missing_fields:
            raise ValueError(f"Missing required fields: {', '.join(missing_fields)}")

        if not isinstance(data_points, list):
            raise ValueError("Data field must be an array")

        if len(data_points) == 0:
            raise ValueError("Data array must be a non-empty list")

        _, trail_id = get_deviceTrail_id(device_id)

        new_body = {
            "trail_id": trail_id,
            "device_id": device_id,
            "battery": battery,
            "data": data_points
        }
        new_event = {**event, "body": json.dumps(new_body)}
        return upload_trail_data(new_event, context)

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

# ========== METADATA ENDPOINTS ==========
def get_trail_metadata(event, context):
    resp = trail_table.scan()
    return {
        "statusCode": 200,
        "headers": cors_headers(),
        "body": json.dumps(convert_decimals(resp.get("Items", [])))
    }


def get_device_metadata(event, context):
    resp = device_table.scan()
    return {
        "statusCode": 200,
        "headers": cors_headers(),
        "body": json.dumps(convert_decimals(resp.get("Items", [])))
    }


def get_trail_groups(event, context):
    resp = trail_group_table.scan()
    return {
        "statusCode": 200,
        "headers": cors_headers(),
        "body": json.dumps(convert_decimals(resp.get("Items", [])))
    }


def create_trail(event, context):
    """
    Create a new trail. Auto-generates trail_id as next available ID.
    Expects: { "trail_name": str, "trail_group": str (optional) }
    Returns: { "trail_id": int, "message": str }
    """
    try:
        body = json.loads(event.get("body", "{}"))

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
                    trail_ids = group.get("trails", [])
                    if not isinstance(trail_ids, list):
                        trail_ids = []
                    if new_trail_id not in trail_ids:
                        trail_ids.append(new_trail_id)
                    trail_group_table.put_item(Item={
                        "name": "All Areas",
                        "trails": trail_ids
                    })
                    all_areas_found = True
                    break

            # If "All Areas" group doesn't exist, create it
            if not all_areas_found:
                trail_group_table.put_item(Item={
                    "name": "All Areas",
                    "trails": [new_trail_id]
                })

            # Step 2: Add to specified trail group if provided (in addition to "All Areas")
            if trail_group and trail_group != "All Areas":
                group_found = False
                for group in groups:
                    if group.get("name") == trail_group:
                        trail_ids = group.get("trails", [])
                        if not isinstance(trail_ids, list):
                            trail_ids = []
                        if new_trail_id not in trail_ids:
                            trail_ids.append(new_trail_id)
                        trail_group_table.put_item(Item={
                            "name": trail_group,
                            "trails": trail_ids
                        })
                        group_found = True
                        break

                if not group_found:
                    trail_group_table.put_item(Item={
                        "name": trail_group,
                        "trails": [new_trail_id]
                    })
        except Exception as e:
            # Continue even if trail group update fails
            pass

        return {
            "statusCode": 200,
            "headers": cors_headers(),
            "body": json.dumps({
                "message": "Trail created successfully",
                "trail_id": new_trail_id
            })
        }
    except Exception as e:
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
        body = json.loads(event.get("body", "{}"))

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
                        trail_ids = group.get("trails", [])
                        if isinstance(trail_ids, list) and trail_id in trail_ids:
                            trail_ids = [tid for tid in trail_ids if tid != trail_id]
                            trail_group_table.put_item(Item={
                                "name": group_name,
                                "trails": trail_ids
                            })

                # Ensure trail is in "All Areas" (all trails should be in this group)
                all_areas_found = False
                for group in groups:
                    if group.get("name") == "All Areas":
                        trail_ids = group.get("trails", [])
                        if not isinstance(trail_ids, list):
                            trail_ids = []
                        if trail_id not in trail_ids:
                            trail_ids.append(trail_id)
                        trail_group_table.put_item(Item={
                            "name": "All Areas",
                            "trails": trail_ids
                        })
                        all_areas_found = True
                        break

                # If "All Areas" doesn't exist, create it
                if not all_areas_found:
                    trail_group_table.put_item(Item={
                        "name": "All Areas",
                        "trails": [trail_id]
                    })

                # Find the target group and add trail_id to it (if not "All Areas")
                if trail_group != "All Areas":
                    group_found = False
                    for group in groups:
                        if group.get("name") == trail_group:
                            trail_ids = group.get("trails", [])
                            if not isinstance(trail_ids, list):
                                trail_ids = []
                            if trail_id not in trail_ids:
                                trail_ids.append(trail_id)
                            trail_group_table.put_item(Item={
                                "name": trail_group,
                                "trails": trail_ids
                            })
                            group_found = True
                            break

                    # If group doesn't exist, create it
                    if not group_found:
                        trail_group_table.put_item(Item={
                            "name": trail_group,
                            "trails": [trail_id]
                        })
            except Exception as e:
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
                        trail_ids = group.get("trails", [])
                        if isinstance(trail_ids, list) and trail_id in trail_ids:
                            trail_ids = [tid for tid in trail_ids if tid != trail_id]
                            trail_group_table.put_item(Item={
                                "name": group_name,
                                "trails": trail_ids
                            })

                # Ensure trail is in "All Areas"
                all_areas_found = False
                for group in groups:
                    if group.get("name") == "All Areas":
                        trail_ids = group.get("trails", [])
                        if not isinstance(trail_ids, list):
                            trail_ids = []
                        if trail_id not in trail_ids:
                            trail_ids.append(trail_id)
                        trail_group_table.put_item(Item={
                            "name": "All Areas",
                            "trails": trail_ids
                        })
                        all_areas_found = True
                        break

                # If "All Areas" doesn't exist, create it
                if not all_areas_found:
                    trail_group_table.put_item(Item={
                        "name": "All Areas",
                        "trails": [trail_id]
                    })
            except Exception as e:
                # Continue even if trail group update fails
                pass

        return {
            "statusCode": 200,
            "headers": cors_headers(),
            "body": json.dumps({"message": "Trail metadata updated successfully"})
        }
    except Exception as e:
        return {
            "statusCode": 500,
            "headers": cors_headers(),
            "body": json.dumps({"error": f"Internal server error: {str(e)}"})
        }


def delete_trail(event, context):
    """
    Delete a trail and all associated data.
    Deletes:
    - Trail metadata
    - All trail device logs for that trail
    - Trail from all trail groups
    - Updates devices associated with this trail to trail_id 0
    Expects: { "trail_id": int }
    """
    try:
        body = json.loads(event.get("body", "{}"))

        trail_id = body.get("trail_id")

        if trail_id is None:
            return {
                "statusCode": 400,
                "headers": cors_headers(),
                "body": json.dumps({"error": "Missing required field: trail_id"})
            }

        try:
            trail_id = int(trail_id)
        except (ValueError, TypeError):
            return {
                "statusCode": 400,
                "headers": cors_headers(),
                "body": json.dumps({"error": "Invalid trail_id format"})
            }

        # Delete all trail device logs for this trail
        try:
            # Query all logs for this trail
            response = logs_table.query(
                KeyConditionExpression=Key("trail_id").eq(trail_id)
            )
            items = response.get("Items", [])

            # Delete all items in batches
            if items:
                with logs_table.batch_writer() as batch:
                    for item in items:
                        batch.delete_item(
                            Key={
                                "trail_id": item["trail_id"],
                                "timestamp": item["timestamp"]
                            }
                        )
        except Exception as e:
            # Log error but continue
            print(f"Error deleting trail logs: {str(e)}")

        # Remove trail from all trail groups
        try:
            resp = trail_groups_table.scan()
            groups = resp.get("Items", [])

            for group in groups:
                trail_ids = group.get("trail_ids", [])
                if isinstance(trail_ids, list) and trail_id in trail_ids:
                    trail_ids = [tid for tid in trail_ids if tid != trail_id]
                    trail_groups_table.put_item(Item={
                        "group_name": group.get("group_name"),
                        "trail_ids": trail_ids
                    })
        except Exception as e:
            # Log error but continue
            print(f"Error removing trail from groups: {str(e)}")

        # Update all devices associated with this trail to trail_id 0
        try:
            resp = device_metadata_table.scan()
            devices = resp.get("Items", [])

            for device in devices:
                if device.get("current_trail_id") == trail_id:
                    device_id = device.get("device_id")
                    battery = device.get("battery")
                    update_device_metadata(device_id, 0, battery)
        except Exception as e:
            # Log error but continue
            print(f"Error updating device associations: {str(e)}")

        # Delete trail metadata
        try:
            trail_metadata_table.delete_item(Key={"trail_id": trail_id})
        except Exception as e:
            return {
                "statusCode": 500,
                "headers": cors_headers(),
                "body": json.dumps({"error": f"Failed to delete trail metadata: {str(e)}"})
            }

        return {
            "statusCode": 200,
            "headers": cors_headers(),
            "body": json.dumps({"message": "Trail and all associated data deleted successfully"})
        }
    except Exception as e:
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
    print(event)
    try:
        body = json.loads(event.get("body", "{}"))

        device_id = body.get("device_id") or 3
        trail_id = body.get("trail_id") or 2
        date_installed = body.get("date_installed")
        date_removed = body.get("date_removed")

        if device_id is None:
            return {
                "statusCode": 400,
                "headers": cors_headers(),
                "body": json.dumps({"error": "Missing required field: device_id"})
            }

        if trail_id is None:
            return {
                "statusCode": 400,
                "headers": cors_headers(),
                "body": json.dumps({"error": "Missing required field: trail_id"})
            }

        if date_installed is None:
            date_installed = int(time.time())
        else:
            date_installed = Decimal(datetime.fromisoformat(date_installed).timestamp())

        if date_removed is None:
            date_removed = int(time.time())
        else:
            date_removed = Decimal(datetime.fromisoformat(date_removed).timestamp())

        try:
            trail_id = int(trail_id)
        except (ValueError, TypeError):
            return {
                "statusCode": 400,
                "headers": cors_headers(),
                "body": json.dumps({"error": "Invalid trail_id format"})
            }

        try:
            device_id = int(device_id)
        except (ValueError, TypeError):
            return {
                "statusCode": 400,
                "headers": cors_headers(),
                "body": json.dumps({"error": "Invalid device_id format"})
            }

        # Find current device_trail_assocation for device_id
        resp = device_trail_table.query(
            KeyConditionExpression=Key("device_id").eq(device_id)
        )
        items = resp.get("Items", [])

        old_device_trail = next((item for item in items if item.get("date_removed") is None), None)
        # If there is an existing device_trail with a different trail_id then consider it removed
        if old_device_trail and old_device_trail["trail_id"] != trail_id:
            device_trail_table.update_item(
                Key={"device_id": device_id, "date_installed": old_device_trail["date_installed"]},
                UpdateExpression="SET date_removed = :date_removed",
                ExpressionAttributeValues={":date_removed": date_removed}
            )

        # If we don't have a current device_trail with this device/trail combo then create a new one
        if not old_device_trail or old_device_trail["trail_id"] != trail_id:
            device_trail_table.put_item(
                Item={
                    "id": get_next_device_trail_id(),
                    "device_id": device_id,
                    "trail_id": trail_id,
                    "date_installed": date_installed,
                }
            )

        return {
            "statusCode": 200,
            "headers": cors_headers(),
            "body": json.dumps({"message": "Device trail association updated successfully"})
        }
    except Exception as e:
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
        # If scan fails, start with ID 1
        new_device_trail_id = 1

    return new_device_trail_id

def cors_headers():
    return {
        "Access-Control-Allow-Origin": "*",
        "Access-Control-Allow-Methods": "GET,POST,PUT,DELETE,OPTIONS",
        "Access-Control-Allow-Headers": "Content-Type,Authorization"
    }