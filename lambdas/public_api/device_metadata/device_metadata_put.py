import json
import time
from datetime import datetime
from decimal import Decimal

from boto3.dynamodb.conditions import Key

from helper_functions import device_trail_table, cors_headers, get_next_device_trail_id

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