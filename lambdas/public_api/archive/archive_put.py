import json
from datetime import datetime

from boto3.dynamodb.conditions import Key

from helper.helper_functions import device_table, device_trail_table, cors_headers


def set_device_archived(event, context):
    """
    Sets the archive status for a device
    Expects: { "device_id": int, "is_archived": bool }
    """
    try:
        print(event)
        body = event.get("body", {})
        if isinstance(body, str):
            body = json.loads(body)

        device_id = body.get("device_id")
        is_archived = body.get("is_archived")

        if device_id is None:
            print("Missing required field: device_id")
            raise ValueError("Missing required field: device_id")

        if is_archived is None:
            print("Missing required field: is_archived")
            raise ValueError("Missing required field: is_archived")

        response = device_table.get_item(Key={"id": int(device_id)})
        if not response.get("Item"):
            print("Device id not found")
            return {
                "statusCode": 404,
                "headers": cors_headers(),
                "body": json.dumps({"error": "Device id not present in table"})
            }

        device_table.update_item(
            Key={"id": int(device_id)},
            UpdateExpression="SET is_archived = :val",
            ExpressionAttributeValues={":val": is_archived}
        )

        if is_archived:
            # get all relevant devicetrail ids for this trail
            date_removed = int(datetime.now().timestamp())
            response = device_trail_table.query(
                KeyConditionExpression=Key("device_id").eq(device_id)
            )
            device_trail_items = response.get("Items", [])

            for device_trail_item in device_trail_items:
                if not device_trail_item.get("date_removed"):
                    device_trail_table.update_item(
                        Key={"device_id": device_trail_item["device_id"], "date_associated": device_trail_item["date_associated"]},
                        UpdateExpression="SET date_removed = :date_removed",
                        ExpressionAttributeValues={":date_removed": date_removed}
                    )

        return {
            "statusCode": 200,
            "headers": cors_headers(),
            "body": json.dumps({"message": f"Device {device_id} is_archived set to {is_archived}"})
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
