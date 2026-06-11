import json

from helper_functions import registration_table, device_table, cors_headers, convert_decimals


def get_registrations(event, context):
    """
    Returns registrations joined with device info. I really really do not want to adjust this later, so I added an
    additionally totally-unnecessary-should-never-be-used param to query a specific reg id.
    Returns data both for the registration table and the device table. I don't know how much ui needs, so chunks of this
    can be cut out if need be, I'd rather give too much and remove lines than have to add more.
    Expects optional query param: registration_id (int)
    """
    try:
        print(event)
        single_params = event.get("queryStringParameters", {}) or {}
        registration_id = single_params.get("registration_id")

        # fetch registration table info
        if registration_id is not None:
            response = registration_table.get_item(Key={"registration_id": int(registration_id)})
            registered_devices = [response["Item"]] if "Item" in response else []
        else:
            registered_devices = registration_table.scan().get("Items", [])

        # join results to device table pieces
        results = []
        for registration in registered_devices:
            device_id = int(registration.get("device_id", 0))
            device_resp = device_table.get_item(Key={"id": device_id})
            device_info = device_resp.get("Item", {})
            results.append({**convert_decimals(registration), "device": convert_decimals(device_info)})

        return {
            "statusCode": 200,
            "headers": cors_headers(),
            "body": json.dumps(results)
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
