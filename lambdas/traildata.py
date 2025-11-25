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
        # Track seen (device_id, timestamp) pairs to filter duplicates
        seen_timestamps = set()
        # Minimum allowed timestamp (1735707600 unix time or January 1, 2025)
        MIN_TIMESTAMP = 1735707600

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

            # Ignore timestamps before minimum allowed time
            if timestamp < MIN_TIMESTAMP:
                continue

            # Check for duplicate timestamp from the same device
            timestamp_key = (device_id, timestamp)
            if timestamp_key in seen_timestamps:
                # Skip duplicate timestamp from same device
                continue
            seen_timestamps.add(timestamp_key)

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
        
        if not trail_name:
            return {
                "statusCode": 400,
                "headers": cors_headers(),
                "body": json.dumps({"error": "Missing required field: trail_name"})
            }
        
        # Get all existing trails to find next available ID
        try:
            resp = trail_metadata_table.scan()
            existing_trails = resp.get("Items", [])
            if existing_trails:
                existing_ids = [int(t.get("trail_id", 0)) for t in existing_trails]
                new_trail_id = max(existing_ids, default=0) + 1
            else:
                new_trail_id = 1
        except Exception as e:
            # If scan fails, start with ID 1
            new_trail_id = 1
        
        # Create trail metadata
        item = {
            "trail_id": new_trail_id,
            "trail_name": str(trail_name)
        }
        
        try:
            trail_metadata_table.put_item(Item=item)
        except Exception as e:
            return {
                "statusCode": 500,
                "headers": cors_headers(),
                "body": json.dumps({"error": f"Failed to create trail: {str(e)}"})
            }
        
        # Always add trail to "All Areas" group
        # Then add to specified group if provided
        try:
            resp = trail_groups_table.scan()
            groups = resp.get("Items", [])
            
            # Step 1: Add to "All Areas" group (all trails should be in this group)
            all_areas_found = False
            for group in groups:
                if group.get("group_name") == "All Areas":
                    trail_ids = group.get("trail_ids", [])
                    if not isinstance(trail_ids, list):
                        trail_ids = []
                    if new_trail_id not in trail_ids:
                        trail_ids.append(new_trail_id)
                    trail_groups_table.put_item(Item={
                        "group_name": "All Areas",
                        "trail_ids": trail_ids
                    })
                    all_areas_found = True
                    break
            
            # If "All Areas" group doesn't exist, create it
            if not all_areas_found:
                trail_groups_table.put_item(Item={
                    "group_name": "All Areas",
                    "trail_ids": [new_trail_id]
                })
            
            # Step 2: Add to specified trail group if provided (in addition to "All Areas")
            if trail_group and trail_group != "All Areas":
                group_found = False
                for group in groups:
                    if group.get("group_name") == trail_group:
                        trail_ids = group.get("trail_ids", [])
                        if not isinstance(trail_ids, list):
                            trail_ids = []
                        if new_trail_id not in trail_ids:
                            trail_ids.append(new_trail_id)
                        trail_groups_table.put_item(Item={
                            "group_name": trail_group,
                            "trail_ids": trail_ids
                        })
                        group_found = True
                        break
                
                if not group_found:
                    trail_groups_table.put_item(Item={
                        "group_name": trail_group,
                        "trail_ids": [new_trail_id]
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
    Expects: { "trail_id": int, "trail_name": str, "trail_group": str }
    """
    try:
        body = json.loads(event.get("body", "{}"))
        
        trail_id = body.get("trail_id")
        trail_name = body.get("trail_name")
        trail_group = body.get("trail_group")
        
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
        item = {"trail_id": trail_id}
        if trail_name is not None:
            item["trail_name"] = str(trail_name)
        
        try:
            trail_metadata_table.put_item(Item=item)
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
                resp = trail_groups_table.scan()
                groups = resp.get("Items", [])
                
                # First, remove trail_id from all other groups (except "All Areas")
                # "All Areas" should always contain all trails
                for group in groups:
                    group_name = group.get("group_name")
                    if group_name != trail_group and group_name != "All Areas":
                        trail_ids = group.get("trail_ids", [])
                        if isinstance(trail_ids, list) and trail_id in trail_ids:
                            trail_ids = [tid for tid in trail_ids if tid != trail_id]
                            trail_groups_table.put_item(Item={
                                "group_name": group_name,
                                "trail_ids": trail_ids
                            })
                
                # Ensure trail is in "All Areas" (all trails should be in this group)
                all_areas_found = False
                for group in groups:
                    if group.get("group_name") == "All Areas":
                        trail_ids = group.get("trail_ids", [])
                        if not isinstance(trail_ids, list):
                            trail_ids = []
                        if trail_id not in trail_ids:
                            trail_ids.append(trail_id)
                        trail_groups_table.put_item(Item={
                            "group_name": "All Areas",
                            "trail_ids": trail_ids
                        })
                        all_areas_found = True
                        break
                
                # If "All Areas" doesn't exist, create it
                if not all_areas_found:
                    trail_groups_table.put_item(Item={
                        "group_name": "All Areas",
                        "trail_ids": [trail_id]
                    })
                
                # Find the target group and add trail_id to it (if not "All Areas")
                if trail_group != "All Areas":
                    group_found = False
                    for group in groups:
                        if group.get("group_name") == trail_group:
                            trail_ids = group.get("trail_ids", [])
                            if not isinstance(trail_ids, list):
                                trail_ids = []
                            if trail_id not in trail_ids:
                                trail_ids.append(trail_id)
                            trail_groups_table.put_item(Item={
                                "group_name": trail_group,
                                "trail_ids": trail_ids
                            })
                            group_found = True
                            break
                    
                    # If group doesn't exist, create it
                    if not group_found:
                        trail_groups_table.put_item(Item={
                            "group_name": trail_group,
                            "trail_ids": [trail_id]
                        })
            except Exception as e:
                # Continue even if trail group update fails
                pass
        else:
            # If trail_group is None (empty string), ensure trail is still in "All Areas"
            # This handles the case when removing a trail from a specific group
            try:
                resp = trail_groups_table.scan()
                groups = resp.get("Items", [])
                
                # Remove from all groups except "All Areas"
                for group in groups:
                    group_name = group.get("group_name")
                    if group_name != "All Areas":
                        trail_ids = group.get("trail_ids", [])
                        if isinstance(trail_ids, list) and trail_id in trail_ids:
                            trail_ids = [tid for tid in trail_ids if tid != trail_id]
                            trail_groups_table.put_item(Item={
                                "group_name": group_name,
                                "trail_ids": trail_ids
                            })
                
                # Ensure trail is in "All Areas"
                all_areas_found = False
                for group in groups:
                    if group.get("group_name") == "All Areas":
                        trail_ids = group.get("trail_ids", [])
                        if not isinstance(trail_ids, list):
                            trail_ids = []
                        if trail_id not in trail_ids:
                            trail_ids.append(trail_id)
                        trail_groups_table.put_item(Item={
                            "group_name": "All Areas",
                            "trail_ids": trail_ids
                        })
                        all_areas_found = True
                        break
                
                # If "All Areas" doesn't exist, create it
                if not all_areas_found:
                    trail_groups_table.put_item(Item={
                        "group_name": "All Areas",
                        "trail_ids": [trail_id]
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
    Update device trail association. Updates DeviceMetadata to change which trail
    a device is associated with. Future data from this device will use the new trail_id.
    Expects: { "device_id": str, "trail_id": int }
    """
    try:
        body = json.loads(event.get("body", "{}"))
        
        device_id = body.get("device_id")
        trail_id = body.get("trail_id")
        
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
        
        try:
            trail_id = int(trail_id)
        except (ValueError, TypeError):
            return {
                "statusCode": 400,
                "headers": cors_headers(),
                "body": json.dumps({"error": "Invalid trail_id format"})
            }
        
        # Update device metadata with new trail_id
        device_id_str = str(device_id)
        
        # Get existing device metadata to preserve battery
        try:
            resp = device_metadata_table.get_item(Key={"device_id": device_id_str})
            existing_item = resp.get("Item", {})
            battery = existing_item.get("battery")
        except Exception:
            battery = None
        
        # Update device metadata
        update_device_metadata(device_id_str, trail_id, battery)
        
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


def cors_headers():
    return {
        "Access-Control-Allow-Origin": "*",
        "Access-Control-Allow-Methods": "GET,POST,PUT,DELETE,OPTIONS",
        "Access-Control-Allow-Headers": "Content-Type,Authorization"
    }