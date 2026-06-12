import json
from helper_functions import device_table, cors_headers


def set_device_blocked(event, context):
    """
    Sets the block status for a device
    Expects: { "device_id": int, "is_blocked": bool }
    """
    try:
        print(event)
        body = event.get("body", {})
        if isinstance(body, str):
            body = json.loads(body)

        device_id = body.get("device_id")
        is_blocked = body.get("is_blocked")

        if device_id is None:
            print("Missing required field: device_id")
            raise ValueError("Missing required field: device_id")

        if is_blocked is None:
            print("Missing required field: is_blocked")
            raise ValueError("Missing required field: is_blocked")

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
            UpdateExpression="SET is_blocked = :val",
            ExpressionAttributeValues={":val": is_blocked}
        )
        return {
            "statusCode": 200,
            "headers": cors_headers(),
            "body": json.dumps({"message": f"Device {device_id} is_blocked set to {is_blocked}"})
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