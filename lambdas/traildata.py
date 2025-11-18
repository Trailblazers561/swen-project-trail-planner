import os
import json
import time
import boto3
from boto3.dynamodb.conditions import Key
from decimal import Decimal

dynamodb = boto3.resource('dynamodb')

# Table references
logs_table = dynamodb.Table(os.environ.get("TRAIL_LOGS_TABLE", "TrailDeviceLogs"))
trail_metadata_table = dynamodb.Table(os.environ.get("TRAIL_METADATA_TABLE", "TrailMetadata"))
device_metadata_table = dynamodb.Table(os.environ.get("DEVICE_METADATA_TABLE", "DeviceMetadata"))
trail_groups_table = dynamodb.Table(os.environ.get("TRAIL_GROUPS_TABLE", "TrailGroups"))

def convert_decimals(obj):
    if isinstance(obj, list):
        return [convert_decimals(i) for i in obj]
    elif isinstance(obj, dict):
        return {k: convert_decimals(v) for k, v in obj.items()}
    elif isinstance(obj, Decimal):
        return float(obj) if obj % 1 > 0 else int(obj)
    else:
        return obj


# ========== GET TRAIL DATA ==========
def get_trail_data(event, context):
    params = event.get('queryStringParameters', {}) or {}
    trails = params.get('trails')
    start = params.get('start')
    end = params.get('end')

    items = []
    if trails:
        trail_ids = [int(t.strip()) for t in trails.split(',')]
        for tid in trail_ids:
            resp = logs_table.query(
                KeyConditionExpression=Key("trail_id").eq(tid)
            )
            items.extend(resp.get("Items", []))
    else:
        resp = logs_table.scan()
        items = resp.get("Items", [])

    return {
        "statusCode": 200,
        "headers": cors_headers(),
        "body": json.dumps(convert_decimals(items))
    }


# ========== UPLOAD TRAIL DATA ==========
def upload_trail_data(event, context):
    body = json.loads(event.get("body", "{}"))
    trail_id_raw = body.get("trail_id")
    data = body.get("data", [])

    if trail_id_raw is None:
        return {
            "statusCode": 400,
            "headers": cors_headers(),
            "body": json.dumps({"error": "Missing required field: trail_id"})
        }

    if not data:
        return {
            "statusCode": 400,
            "headers": cors_headers(),
            "body": json.dumps({"error": "Data array cannot be empty"})
        }

    try:
        trail_id = int(trail_id_raw)
    except (ValueError, TypeError):
        return {
            "statusCode": 400,
            "headers": cors_headers(),
            "body": json.dumps({"error": "Invalid data format: trail_id must be an integer"})
        }

    with logs_table.batch_writer() as batch:
        for idx, point in enumerate(data):
            timestamp_raw = point.get("timestamp") or point.get("ts")
            device_id = point.get("device_id") or body.get("device_id")

            missing = []
            if timestamp_raw is None:
                missing.append("timestamp")
            if device_id is None:
                missing.append("device_id")

            if missing:
                return {
                    "statusCode": 400,
                    "headers": cors_headers(),
                    "body": json.dumps({"error": f"Missing required fields (data[{idx}]): {', '.join(missing)}"})
                }

            try:
                timestamp = int(timestamp_raw)
            except (ValueError, TypeError):
                return {
                    "statusCode": 400,
                    "headers": cors_headers(),
                    "body": json.dumps({"error": f"Invalid timestamp format (data[{idx}])"})
                }

            item = {
                "trail_id": trail_id,
                "timestamp": timestamp,
                "device_id": device_id,
            }

            base_battery = point.get("battery", body.get("battery"))
            if base_battery is not None:
                item["battery"] = Decimal(str(base_battery)) if isinstance(base_battery, float) else base_battery

            for key, value in point.items():
                if key in ["timestamp", "ts", "device_id"]:
                    continue
                if isinstance(value, float):
                    item[key] = Decimal(str(value))
                else:
                    item[key] = value

            batch.put_item(Item=item)

    return {
        "statusCode": 200,
        "headers": cors_headers(),
        "body": json.dumps({"message": "Trail data uploaded"})
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
    The server automatically determines trail_id if not provided by:
    1. Using trail_id from payload if provided
    2. Checking DeviceMetadata table
    3. Querying most recent entry in TrailDeviceLogs for that device
    4. Defaulting to trail_id 1 for new devices
    """
    try:
        body = json.loads(event.get("body", "{}"))

        if not body:
            return {
                "statusCode": 400,
                "headers": cors_headers(),
                "body": json.dumps({"error": "Request body cannot be empty"})
            }

        device_id_raw = body.get("device_id")
        device_id = str(device_id_raw) if device_id_raw is not None else None
        data_points = body.get("data")
        battery = body.get("battery")
        trail_id_override = body.get("trail_id")

        missing_fields = []
        if not device_id:
            missing_fields.append("device_id")
        if data_points is None:
            missing_fields.append("data")

        if missing_fields:
            return {
                "statusCode": 400,
                "headers": cors_headers(),
                "body": json.dumps({"error": f"Missing required fields: {', '.join(missing_fields)}"})
            }

        if not isinstance(data_points, list):
            return {
                "statusCode": 400,
                "headers": cors_headers(),
                "body": json.dumps({"error": "Data field must be an array"})
            }

        if len(data_points) == 0:
            return {
                "statusCode": 400,
                "headers": cors_headers(),
                "body": json.dumps({"error": "Data array must be a non-empty list"})
            }

        # Determine trail_id using automatic resolution
        resolved_trail_id = None
        if trail_id_override is not None:
            try:
                resolved_trail_id = int(trail_id_override)
            except (ValueError, TypeError):
                return {
                    "statusCode": 400,
                    "headers": cors_headers(),
                    "body": json.dumps({"error": "Invalid data format: trail_id must be an integer"})
                }
        else:
            # Auto-resolve trail_id: check metadata, then logs, then default
            try:
                resolved_trail_id = resolve_trail_id_for_device(device_id)
                # Update DeviceMetadata with resolved trail_id for future requests
                update_device_metadata(device_id, resolved_trail_id, battery)
            except Exception as e:
                # If resolution fails, default to 0
                resolved_trail_id = 0
                update_device_metadata(device_id, resolved_trail_id, battery)
        
        # Ensure resolved_trail_id is set (should never be None at this point)
        if resolved_trail_id is None:
            resolved_trail_id = 0

        prepared_items = []

        for idx, point in enumerate(data_points):
            timestamp_raw = point.get("ts") or point.get("timestamp")
            point_trail_raw = point.get("trail_id")

            if timestamp_raw is None:
                return {
                    "statusCode": 400,
                    "headers": cors_headers(),
                    "body": json.dumps({"error": f"Missing required field ts (data[{idx}])"})
                }

            try:
                timestamp = int(timestamp_raw)
            except (ValueError, TypeError):
                return {
                    "statusCode": 400,
                    "headers": cors_headers(),
                    "body": json.dumps({"error": f"Invalid timestamp format (data[{idx}])"})
                }

            # Per-point trail_id override takes precedence
            if point_trail_raw is not None:
                try:
                    trail_id = int(point_trail_raw)
                except (ValueError, TypeError):
                    return {
                        "statusCode": 400,
                        "headers": cors_headers(),
                        "body": json.dumps({"error": f"Invalid trail_id format (data[{idx}])"})
                    }
            else:
                trail_id = resolved_trail_id

            item = {
                "trail_id": trail_id,
                "timestamp": timestamp,
                "device_id": device_id,
            }

            # Determine battery priority: per-point > request-level
            point_battery = point.get("battery")
            battery_value = point_battery if point_battery is not None else battery
            if battery_value is not None:
                item["battery"] = Decimal(str(battery_value)) if isinstance(battery_value, float) else battery_value

            for key, value in point.items():
                if key in ["ts", "timestamp", "trail_id"]:
                    continue
                if isinstance(value, float):
                    item[key] = Decimal(str(value))
                else:
                    item[key] = value

            prepared_items.append(item)

        if len(prepared_items) == 1:
            logs_table.put_item(Item=prepared_items[0])
        else:
            with logs_table.batch_writer() as batch:
                for item in prepared_items:
                    batch.put_item(Item=item)

        return {
            "statusCode": 200,
            "headers": cors_headers(),
            "body": json.dumps({"message": "Device data uploaded successfully"})
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


def resolve_trail_id_for_device(device_id):
    """
    Automatically resolve trail_id for a device using this priority:
    1. Check DeviceMetadata table
    2. Query most recent entry in TrailDeviceLogs for that device
    3. Default to trail_id 1 for new devices
    """
    device_id_str = str(device_id)
    
    # First, try DeviceMetadata
    try:
        resp = device_metadata_table.get_item(Key={"device_id": device_id_str})
        item = resp.get("Item")
        if item and "current_trail_id" in item:
            try:
                return int(item["current_trail_id"])
            except (ValueError, TypeError):
                pass  # Invalid format, continue to next method
    except Exception:
        pass  # Continue to next method if lookup fails
    
    # Second, query TrailDeviceLogs for most recent entry using GSI
    try:
        resp = logs_table.query(
            IndexName="device_id-timestamp-index",
            KeyConditionExpression=Key("device_id").eq(device_id_str),
            ScanIndexForward=False,  # Descending order (most recent first)
            Limit=1
        )
        items = resp.get("Items", [])
        if items and "trail_id" in items[0]:
            try:
                return int(items[0]["trail_id"])
            except (ValueError, TypeError):
                pass  # Invalid format, continue to default
    except Exception:
        pass  # Continue to default if query fails
    
    # Default to trail_id 0 for new devices
    return 0


def update_device_metadata(device_id, trail_id, battery=None):
    """
    Update or create DeviceMetadata entry for a device.
    This caches the trail_id for faster lookups on future requests.
    """
    device_id_str = str(device_id)
    item = {
        "device_id": device_id_str,
        "current_trail_id": trail_id,
    }
    
    if battery is not None:
        item["battery"] = Decimal(str(battery)) if isinstance(battery, float) else battery
    
    # Add last_update timestamp
    item["last_update"] = int(time.time())
    
    try:
        device_metadata_table.put_item(Item=item)
    except Exception:
        # Silently fail - metadata update is not critical for data upload
        pass


# ========== METADATA ENDPOINTS ==========
def get_trail_metadata(event, context):
    resp = trail_metadata_table.scan()
    return {
        "statusCode": 200,
        "headers": cors_headers(),
        "body": json.dumps(convert_decimals(resp.get("Items", [])))
    }

def get_device_metadata(event, context):
    resp = device_metadata_table.scan()
    return {
        "statusCode": 200,
        "headers": cors_headers(),
        "body": json.dumps(convert_decimals(resp.get("Items", [])))
    }

def get_trail_groups(event, context):
    resp = trail_groups_table.scan()
    return {
        "statusCode": 200,
        "headers": cors_headers(),
        "body": json.dumps(convert_decimals(resp.get("Items", [])))
    }

def cors_headers():
    return {
        "Access-Control-Allow-Origin": "*",
        "Access-Control-Allow-Methods": "GET,POST,OPTIONS",
        "Access-Control-Allow-Headers": "Content-Type,Authorization"
    }