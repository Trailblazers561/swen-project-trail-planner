import json
from helper_functions import device_table, cors_headers


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
            return {
                "statusCode": 400,
                "headers": cors_headers(),
                "body": json.dumps({"error": "Missing required field: device_id"})
            }

        if is_archived is None:
            print("Missing required field: is_archived")
            return {
                "statusCode": 400,
                "headers": cors_headers(),
                "body": json.dumps({"error": "Missing required field: is_archived"})
            }

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
