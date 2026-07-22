import json
from collections import defaultdict
from datetime import datetime, timedelta

from boto3.dynamodb.conditions import Key

from helper.helper_functions import device_trail_log_hour_table, device_trail_log_day_table, \
    device_trail_log_week_table, \
    device_trail_log_month_table, device_table, device_trail_table, device_log_table, cors_headers, get_device_trail_id, \
    timestamp_conversion, is_device_blocked, is_device_archived, upload_trail_data


def upload_device_data(event, context):
    """
    Handle PUT requests from devices to /devices/ endpoint.
    Supports compact payloads such as:
    {
        "name": "deviceA",
        "battery": 94,
        "data": [{"timestamp": 1767243600, "count": 184}],
        "firmware_version": "1.2.17"
        "rssi": -61
        "rsrp": -97
        "rsrq": -7
        "unitTestMode": true
    }
    A device should be registered in the system before using this.
    unitTestMode is an OPTIONAL value that should NOT be sent by a normal device. It is exclusively a test mode flag
    for the device emulator to get around some of the safeguards that a normal device has on ensuring clean data.
    """
    try:
        print(event)
        body = event.get("body", "{}")
        if isinstance(body, str):
            body = json.loads(body)

        if not body:
            raise ValueError("Request body cannot be empty")

        name = body.get("name")
        if not name:
            raise ValueError("Missing required field: name")

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
            raise ValueError("Device certificate information does not match the requested device for data upload")

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

        data_points = body.get("data")
        battery = body.get("battery")
        firmware_version = body.get("firmware_version")
        rssi = body.get("rssi")
        rsrp = body.get("rsrp")
        rsrq = body.get("rsrq")

        testFlag = body.get("unitTestMode") is True

        if not data_points: raise ValueError("Missing required field: data_points")
        if battery is None: raise ValueError("Missing required field: battery")

        device_exists = device_table.query(
            IndexName="name-index",
            KeyConditionExpression=Key("name").eq(name),
            Limit=1
        )["Items"]
        device_id = device_exists[0]["id"] if device_exists else None
        if not device_id: raise ValueError(
            f"Cannot find device with name [{name}], please register if not done already")

        if not isinstance(data_points, list):
            raise ValueError("Data field must be an array")

        total = 0
        for point in data_points:
            if "count" not in point:
                raise ValueError("Data points must have count attribute")
            if "timestamp" not in point and "ts" not in point:
                raise ValueError("Data points must have ts or timestamp attribute")
            total += point["count"]

        device_log_table.put_item(Item={
            "device_id": device_id,
            "time": int(datetime.now().timestamp()),
            "log_type": "data_upload",
            "count": total,
            "battery": battery,
            "firmware_version": firmware_version,
            "rssi": rssi,
            "rsrp": rsrp,
            "rsrq": rsrq
        })

        print(f"Attempting to upload data of device [{device_id}] with data [{data_points}] and battery [{battery}]")

        device_trail_results = device_trail_table.query(
            KeyConditionExpression=Key("device_id").eq(device_id),
            ScanIndexForward=False,
            Limit=1
        ).get("Items", [])

        if not device_trail_results or "date_retired" in device_trail_results[0]:
            return {
                "statusCode": 202,
                "headers": cors_headers(),
                "body": json.dumps({"message": f"Device request logged, but must be associated to a trail to log data"})
            }

        if "date_installed" not in device_trail_results[0]:
            return {
                "statusCode": 202,
                "headers": cors_headers(),
                "body": json.dumps({"message": f"Device request logged, but must be marked as installed to log data"})
            }

        trail_id = device_trail_results[0]["trail_id"]
        date_installed = device_trail_results[0]["date_installed"]

        if testFlag:
            new_data_points = data_points
        else:
            minimum_date = (datetime.fromtimestamp(int(date_installed)).replace(minute=0, second=0,
                                                                                microsecond=0) + timedelta(
                hours=1)).timestamp()
            new_data_points = [data_point for data_point in data_points if
                               data_point.get("ts", 0) >= minimum_date or data_point.get("timestamp",
                                                                                         0) >= minimum_date]

        if new_data_points:
            new_body = {
                "trail_id": trail_id,
                "device_id": device_id,
                "battery": battery,
                "data": new_data_points
            }
            new_event = {**event, "body": new_body}

            upload_trail_data_call = upload_trail_data(new_event, context)
            if upload_trail_data_call["statusCode"] != 200:
                return upload_trail_data_call

        return {
            "statusCode": 200,
            "headers": cors_headers(),
            "body": json.dumps({"message": "Device data uploaded successfully"})
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



