import json
from datetime import datetime
from decimal import Decimal

from boto3.dynamodb.conditions import Key

from helper.helper_functions import device_table, cors_headers, is_device_blocked, is_device_archived


def upload_device_info(event, context):
    """
    Handle POST requests from devices to /devices/ endpoint
    Turns the stubbed device table entry into a more fleshed out version. Devices can call this when they're registered
    as a tester to ensure they're actually connected. The server can pick this up and the device can see the 200 response.
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

        if name is None:
            raise ValueError("Missing required field: name")
        if firmware_version is None:
            raise ValueError("Missing required field: firmware_version")
        if date_manufactured is None:
            raise ValueError("Missing required field: date_manufactured")

        # extract certificate info out of mtls pieces
        cert_subject = event.get("requestContext", {}).get("identity", {}).get("clientCert", {}).get("subjectDN")
        if not cert_subject:
            raise ValueError("No client certificate presented")

        # extract device name out of cert info common name field
        cert_device_name = None
        for part in cert_subject.split(","):
            if part.strip().startswith("CN="):
                cert_device_name = part.strip()[3:]
                break

        # passed in name should match the name on the cert
        if cert_device_name != name:
            raise ValueError("Device certificate information does not match the requested device for data test")

        # assume device isn't blocked by our system
        if is_device_blocked(device_name=name):
            return {
                "statusCode": 403,
                "headers": cors_headers(),
                "body": json.dumps({"error": "Device is blocked. Info upload rejected."})
            }

        # assume device isn't archived in our system
        if is_device_archived(device_name=name):
            return {
                "statusCode": 403,
                "headers": cors_headers(),
                "body": json.dumps({"error": "Device is archived. Info upload rejected."})
            }

        response = device_table.query(IndexName="name-index", KeyConditionExpression=Key("name").eq(name), Limit=1).get(
            "Items", [])
        if not response:
            print("Device name linked to device table entry not found")
            return {
                "statusCode": 404,
                "headers": cors_headers(),
                "body": json.dumps({"error": "Device id liked to registration entry not found"})
            }
        device_id = response[0].get("id")

        date_manufactured = Decimal(datetime.fromisoformat(date_manufactured).timestamp())
        print(
            f"Attempting to update device data- firmware_version [{firmware_version}], date_manufactured [{date_manufactured}], notes [{notes}]")

        update_values = "SET firmware_version = :fv, date_manufactured = :dm"
        expression_values = {":fv": firmware_version, ":dm": date_manufactured}

        if notes:
            update_values += ", notes = :notes"
            expression_values[":notes"] = notes

        device_table.update_item(
            Key={"id": int(device_id)},
            UpdateExpression=update_values,
            ExpressionAttributeValues=expression_values
        )

        print(f"Successfully updated device with id [{device_id}]")
        return {
            "statusCode": 200,
            "headers": cors_headers(),
            "body": json.dumps({
                "message": "Device info updated successfully",
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
