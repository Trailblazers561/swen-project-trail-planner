import json
from collections import defaultdict
from decimal import Decimal

from helper_functions import device_trail_log_hour_table, device_trail_log_day_table, device_trail_log_week_table, device_trail_log_month_table, cors_headers, get_device_trail_id, timestamp_conversion

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
        daily_logs = defaultdict(lambda: {"count": 0, "latest_timestamp": 0, "battery": None})
        weekly_logs = defaultdict(lambda: {"count": 0, "latest_timestamp": 0, "battery": None})
        monthly_logs = defaultdict(lambda: {"count": 0, "latest_timestamp": 0, "battery": None})
        row_data: dict[tuple, dict] = {}

        # some input validation and loading data into a format we can load into table
        for idx, point in enumerate(data):
            timestamp_raw = point.get("timestamp") or point.get("ts")
            device_id = point.get("device_id") or body.get("device_id")
            count = point.get("count") or body.get("count")
            battery = point.get("battery", body.get("battery"))

            missing = []
            if timestamp_raw is None:
                missing.append("timestamp")
            if device_id is None:
                missing.append("device_id")
            if count is None:
                missing.append("count")
            if battery is None:
                missing.append("battery")

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

            battery = Decimal(str(battery)) if isinstance(battery, float) else battery

            timestamp_key = (device_id, timestamp)
            row_data[timestamp_key] = {"count": count, "battery": battery}

        device_trail_id_cache = {}
        for (device_id, hour_ts), data in row_data.items():
            hour_ts = timestamp_conversion(hour_ts, "hour")
            if device_id not in device_trail_id_cache:
                device_trail_id_cache[device_id] = get_device_trail_id(device_id, trail_id)[0]
            device_trail_id = device_trail_id_cache[device_id]

            current_day = (device_trail_id, timestamp_conversion(hour_ts, "day"))
            current_week = (device_trail_id, timestamp_conversion(hour_ts, "week"))
            current_month = (device_trail_id, timestamp_conversion(hour_ts, "month"))

            # populate counts/battery %s on the daily/weekly/monthly levels
            daily_logs[current_day]["count"] += data["count"]
            if hour_ts > daily_logs[current_day]["latest_timestamp"] and data["battery"] is not None:
                daily_logs[current_day]["battery"] = data["battery"]
                daily_logs[current_day]["latest_timestamp"] = hour_ts

            weekly_logs[current_week]["count"] += data["count"]
            if hour_ts > weekly_logs[current_week]["latest_timestamp"] and data["battery"] is not None:
                weekly_logs[current_week]["battery"] = data["battery"]
                weekly_logs[current_week]["latest_timestamp"] = hour_ts

            monthly_logs[current_month]["count"] += data["count"]
            if hour_ts > monthly_logs[current_month]["latest_timestamp"] and data["battery"] is not None:
                monthly_logs[current_month]["battery"] = data["battery"]
                monthly_logs[current_month]["latest_timestamp"] = hour_ts

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
                    "count": data["count"],
                    "battery": data["battery"] if data["battery"] is not None else ""
                })
        print(f"writing {len(daily_logs)} to day database")

        # Send data to week table
        with device_trail_log_week_table.batch_writer() as batch:
            for (device_trail_id, week_ts), data in weekly_logs.items():
                batch.put_item(Item={
                    "device_trail_id": device_trail_id,
                    "start": week_ts,
                    "count": data["count"],
                    "battery": data["battery"] if data["battery"] is not None else ""
                })
        print(f"writing {len(weekly_logs)} to week database")

        # Send data to month table
        with device_trail_log_month_table.batch_writer() as batch:
            for (device_trail_id, month_ts), data in monthly_logs.items():
                batch.put_item(Item={
                    "device_trail_id": device_trail_id,
                    "start": month_ts,
                    "count": data["count"],
                    "battery": data["battery"] if data["battery"] is not None else ""
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