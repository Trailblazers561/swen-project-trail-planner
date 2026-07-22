import json
import uuid
from datetime import datetime, timedelta

from helper.helper_functions import cors_headers, is_device_blocked, is_device_archived, v1_device_bucket, s3_client


def upload_adapted_device_data(event, context):
    """
    Handle POST requests from the old device to the /adapter/ endpoint.
    Supports compact payloads such as:
    {
      "device_id": <string>,
      "firmware_version": <string>,
      "rssi": <int>,
      "rsrp": <float>,
      "rsrq": <float>,
      "battery": <uint>,
      "supply_mv": <uint>,
      "data": [
        { "ts": <uint32 unix timestamp> },
        ...
      ]
    }
    This is for the SINGLE special device that should exist in the system as a means of backwards compatibility.
    Accumulates the individual hiker data points in an s3 bucket to be batch processed later(once a day, simulating a real device).
    """
    try:
        print(event)
        body = event.get("body", "{}")
        if isinstance(body, str):
            body = json.loads(body)

        if not body:
            raise ValueError("Request body cannot be empty")

        cert_subject = event.get("requestContext", {}).get("identity", {}).get("clientCert", {}).get("subjectDN")
        if not cert_subject:
            raise ValueError("No client certificate presented")

        # they're the same thing
        name = body.get("device_id")
        if not name:
            raise ValueError("Missing required field: device_id")

        # assume device isn't blocked by our system
        if is_device_blocked(device_name=name):
            return {
                "statusCode": 403,
                "headers": cors_headers(),
                "body": json.dumps({"error": "Device is blocked. Data upload rejected."})
            }

        # assume device isn't archived in our system
        if is_device_archived(device_name=name):
            return {
                "statusCode": 403,
                "headers": cors_headers(),
                "body": json.dumps({"error": "Device is archived. Data upload rejected."})
            }

        data_points = body.get("data", [])

        device_data = {
            "device_name": name,
            "battery": body.get("battery"),
            "firmware_version": body.get("firmware_version"),
            "rssi": body.get("rssi"),
            "rsrp": body.get("rsrp"),
            "rsrq": body.get("rsrq"),
            "supply_mv": body.get("supply_mv"),
            "hits": [entry.get("ts") for entry in data_points if entry.get("ts") is not None],
            "received_at": datetime.utcnow().isoformat(),
        }

        key = f"buffer/{uuid.uuid4().hex}.json"
        s3_client.put_object(Bucket=v1_device_bucket, Key=key, Body=json.dumps(device_data).encode())

        return {
            "statusCode": 200,
            "headers": cors_headers(),
            "body": json.dumps({"message": "Device data stored successfully"})
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
