import json
from datetime import datetime
from decimal import Decimal

from helper_functions import device_table, cors_headers, get_next_device_id

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