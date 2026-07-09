import json
from collections import defaultdict
from datetime import datetime, timedelta

from boto3.dynamodb.conditions import Key

from helper.helper_functions import device_trail_log_hour_table, device_trail_log_day_table, device_trail_log_week_table, \
    device_trail_log_month_table, device_table, device_trail_table, device_log_table, cors_headers, get_device_trail_id, \
    timestamp_conversion, is_device_blocked, is_device_archived

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
    }
    A device should be registered in the system before using this.
    """
    try:
        print(event)
        body = event.get("body","{}")
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

        # TODO: figure this out thanks nico
        if not (data_points and battery): raise ValueError("Missing required field: data_points and battery")

        device_exists = device_table.query(
            IndexName="name-index",
            KeyConditionExpression=Key("name").eq(name),
            Limit=1
        )["Items"]
        device_id = device_exists[0]["id"] if device_exists else None
        if not device_id: raise ValueError(f"Cannot find device with name [{name}], please register if not done already")

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

        print(f"Attempting to upload data of device [{device_id}] to with data [{data_points}] and battery [{battery}]")

        device_trail_results = device_trail_table.query(
            KeyConditionExpression=Key("device_id").eq(device_id),
            ScanIndexForward=False,
            Limit=1
        ).get("Items", [])

        if not device_trail_results or "date_retired" in device_trail_results[0]:
            return {
                "statusCode": 200, #TODO: this status code?
                "headers": cors_headers(),
                "body": json.dumps({"message": f"Device request logged, but must be associated to a trail to log data"})
            }

        if "date_installed" not in device_trail_results[0]:
            return {
                "statusCode": 200, #TODO: this status code?
                "headers": cors_headers(),
                "body": json.dumps({"message": f"Device request logged, but must be marked as installed to log data"})
            }

        trail_id = device_trail_results[0]["trail_id"]
        date_installed = device_trail_results[0]["date_installed"]

        minimum_date = (datetime.fromtimestamp(int(date_installed)).replace(minute=0,second=0,microsecond=0) + timedelta(hours=1)).timestamp()
        new_data_points = [data_point for data_point in data_points if data_point.get("ts", 0) >= minimum_date or data_point.get("timestamp", 0) >= minimum_date]

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

def upload_trail_data(event, context):
    try:
        body = event.get("body", {})
        if isinstance(body, str):
            body = json.loads(body)
        trail_id_raw = body.get("trail_id")
        data = body.get("data", [])

        if trail_id_raw is None:
            raise ValueError("Missing required field: trail_id")

        if not data:
            raise ValueError("Data array cannot be empty")

        trail_id = int(trail_id_raw)

        # Build data structures for day/week/month
        daily_logs = defaultdict(lambda: {"count": 0})
        weekly_logs = defaultdict(lambda: {"count": 0})
        monthly_logs = defaultdict(lambda: {"count": 0})
        row_data: dict[tuple, dict] = {}

        # some input validation and loading data into a format we can load into table
        for idx, point in enumerate(data):
            timestamp_raw = point.get("timestamp") or point.get("ts")
            device_id = point.get("device_id") or body.get("device_id")
            count = point.get("count") or body.get("count")

            missing = []
            if timestamp_raw is None:
                missing.append("timestamp")
            if device_id is None:
                missing.append("device_id")
            if count is None:
                missing.append("count")

            if missing:
                raise ValueError(f"Missing required fields (data[{idx}]): {', '.join(missing)}")

            try:
                timestamp = int(timestamp_raw)
            except (ValueError, TypeError):
                return {
                    "statusCode": 400,
                    "headers": cors_headers(),
                    "body": json.dumps({"error": f"Invalid timestamp format (data[{idx}])"})
                }

            timestamp_key = (device_id, timestamp)
            row_data[timestamp_key] = {"count": count}

        device_trail_id_cache = {}
        for (device_id, hour_ts), data in row_data.items():
            hour_ts = timestamp_conversion(hour_ts, "hour")
            if device_id not in device_trail_id_cache:
                device_trail_id_cache[device_id] = get_device_trail_id(device_id, trail_id)[0]
            device_trail_id = device_trail_id_cache[device_id]

            current_day = (device_trail_id, timestamp_conversion(hour_ts, "day"))
            current_week = (device_trail_id, timestamp_conversion(hour_ts, "week"))
            current_month = (device_trail_id, timestamp_conversion(hour_ts, "month"))

            # populate counts on the daily/weekly/monthly levels
            daily_logs[current_day]["count"] += data["count"]
            weekly_logs[current_week]["count"] += data["count"]
            monthly_logs[current_month]["count"] += data["count"]

        # Send data to hour table
        with device_trail_log_hour_table.batch_writer() as batch:
            for (device_id, hour_ts), data in row_data.items():
                batch.put_item(Item={
                    "device_trail_id": device_trail_id_cache[device_id],
                    "start": hour_ts,
                    "count": data["count"],
                })
        print(f"writing {len(row_data)} to hour database")

        # Send data to day table
        with device_trail_log_day_table.batch_writer() as batch:
            for (device_trail_id, day_ts), data in daily_logs.items():
                batch.put_item(Item={
                    "device_trail_id": device_trail_id,
                    "start": day_ts,
                    "count": data["count"]
                })
        print(f"writing {len(daily_logs)} to day database")

        # Send data to week table
        with device_trail_log_week_table.batch_writer() as batch:
            for (device_trail_id, week_ts), data in weekly_logs.items():
                batch.put_item(Item={
                    "device_trail_id": device_trail_id,
                    "start": week_ts,
                    "count": data["count"]
                })
        print(f"writing {len(weekly_logs)} to week database")

        # Send data to month table
        with device_trail_log_month_table.batch_writer() as batch:
            for (device_trail_id, month_ts), data in monthly_logs.items():
                batch.put_item(Item={
                    "device_trail_id": device_trail_id,
                    "start": month_ts,
                    "count": data["count"]
                })
        print(f"writing {len(monthly_logs)} to month database")

        return {
            "statusCode": 200,
            "headers": cors_headers(),
            "body": json.dumps({"message": "Trail data uploaded"})
        }
    except ValueError as e:
        print(e)
        return {
            "statusCode": 400,
            "headers": cors_headers(),
            "body": json.dumps({"error": str(e)})
        }
    except Exception as e:
        print(e)
        return {
            "statusCode": 500,
            "headers": cors_headers(),
            "body": json.dumps({"error": f"Internal server error: {str(e)}"})
        }