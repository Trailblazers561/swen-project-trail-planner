import json
import time
from datetime import datetime
from decimal import Decimal

from boto3.dynamodb.conditions import Key

from helper.helper_functions import device_trail_table, cors_headers, get_next_device_trail_id

def update_device_trail_association(event, context):
    """
    Update device trail association. Updates DeviceTrail to change which trail
    a device is associated with. Future data from this device will use the new trail_id. Unpairs device if trail_id=0
    Expects: { "device_id": str, "trail_id": int }
    """
    try:
        print(event)
        body = event.get("body", {})
        if isinstance(body, str):
            body = json.loads(body)

        device_id = body.get("device_id")
        trail_id = body.get("trail_id")

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

        now = int(time.time())

        print(f"Attempting to update device_trail_association with device_id [{device_id}] and trail_id [{trail_id}] at time [{now}]")

        # Find current device_trail_assocation for device_id
        resp = device_trail_table.query(
            KeyConditionExpression=Key("device_id").eq(device_id)
        )
        items = resp.get("Items", [])

        old_device_trail_by_device = next((item for item in items if item.get("date_removed") is None), None)

        # If there is an existing device_trail that hasn't yet been installed
        if old_device_trail_by_device and old_device_trail_by_device["trail_id"] == trail_id:
            if old_device_trail_by_device.get("date_installed") is not None:
                raise ValueError("This device is already installed on this trail, nothing to update")
            device_trail_table.update_item(
                Key={"device_id": device_id, "date_associated": old_device_trail_by_device["date_associated"]},
                UpdateExpression="SET date_installed = :date_installed",
                ExpressionAttributeValues={":date_installed": now}
            )
            print("Successfully updated device trail association")
            return {
                "statusCode": 200,
                "headers": cors_headers(),
                "body": json.dumps({"message": "Device trail association updated successfully"})
            }

        # If there is an existing device_trail with a different trail_id then consider it removed
        if old_device_trail_by_device and old_device_trail_by_device["trail_id"] != trail_id:
            print(f"Setting old device_trail_association [{old_device_trail_by_device['id']}] to removed ")
            device_trail_table.update_item(
                Key={"device_id": device_id, "date_associated": old_device_trail_by_device["date_associated"]},
                UpdateExpression="SET date_removed = :date_removed",
                ExpressionAttributeValues={":date_removed": now}
            )

        if trail_id:
            # Find current device_trail_assocation for trail_id
            resp = device_trail_table.query(
                IndexName="trail-index",
                KeyConditionExpression=Key("trail_id").eq(trail_id)
            )
            items = resp.get("Items", [])

            old_device_trail_by_trail = next((item for item in items if item.get("date_removed") is None), None)
            # If there is an existing device_trail with a different device_id then consider it removed
            if old_device_trail_by_trail and old_device_trail_by_trail["device_id"] != device_id:
                print(f"Setting old device_trail_association [{old_device_trail_by_trail['id']}] to removed ")
                device_trail_table.update_item(
                    Key={"device_id": old_device_trail_by_trail["device_id"], "date_associated": old_device_trail_by_trail["date_associated"]},
                    UpdateExpression="SET date_removed = :date_removed",
                    ExpressionAttributeValues={":date_removed": now}
                )

        # If we don't have a current device_trail with this device/trail combo then create a new one
        if (not old_device_trail_by_device or old_device_trail_by_device["trail_id"] != trail_id) and trail_id:
            next_device_trail_id = get_next_device_trail_id()
            print(f"Creating new device_trail log with id [{next_device_trail_id}]")
            device_trail_table.put_item(
                Item={
                    "id": next_device_trail_id,
                    "device_id": device_id,
                    "trail_id": trail_id,
                    "date_associated": now,
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