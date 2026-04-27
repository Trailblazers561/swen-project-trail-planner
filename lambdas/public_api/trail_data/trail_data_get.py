import json
from datetime import datetime, timedelta
from decimal import Decimal
from zoneinfo import ZoneInfo

from boto3.dynamodb.conditions import Key

from helper_functions import device_trail_log_day_table, device_trail_table, table_time_map, convert_decimals, cors_headers

def get_trail_data(event, context):
    try:
        print(event)
        single_params = event.get("queryStringParameters", {}) or {}
        multi_params = event.get("multiValueQueryStringParameters", {}) or {}

        trail_id_list = multi_params.get('trail_id')
        start_time = single_params.get("start_time")
        end_time = single_params.get("end_time")
        granularity = single_params.get("granularity", "day")

        if trail_id_list is None: raise ValueError("Missing required field(s): trail_id")
        if not all(id.isdigit() for id in trail_id_list): raise ValueError("Invalid trail_id_list format")
        trail_id_list_decimals = [Decimal(id) for id in trail_id_list]

        if not start_time: raise ValueError("Missing required field: start_time")
        if not end_time: raise ValueError("Missing required field: end_time")

        print(f"Attempting to retrieve logs for trails [{trail_id_list_decimals}], from [{start_time}] to [{end_time}] at granularity of [{granularity}]")

        if granularity not in table_time_map:
            logs_time_table = table_time_map["day"]
        else:
            logs_time_table = table_time_map[granularity]

        device_trail_ids = []
        device_trail_cache = {}

        start_time = datetime.fromisoformat(start_time).astimezone(ZoneInfo("America/New_York"))
        end_time = datetime.fromisoformat(end_time).astimezone(ZoneInfo("America/New_York"))

        # Add a day to end_time (since we subtract 1 from the timestamp this won't add a real day's data)
        if granularity == "hour":
            end_time = (end_time + timedelta(hours=1)).replace(minute=0, second=0)
        else:
            end_time = (end_time + timedelta(days=1)).replace(hour=0, minute=0, second=0)

        if granularity in ("week", "month"):
            partial_start_timestamp = int(start_time.timestamp())
            partial_end_timestamp = int(end_time.timestamp())
            if granularity == "week":
                query_start_timestamp = int((start_time + timedelta(days=(7 - start_time.weekday()) % 7)).timestamp())
                query_end_timestamp = int((end_time - timedelta(days=end_time.weekday())).timestamp())
            if granularity == "month":
                query_start_timestamp = int((start_time if start_time.day == 1 else (start_time.replace(day=28) + timedelta(days=4)).replace(day=1)).timestamp())
                query_end_timestamp = int(end_time.replace(day=1).timestamp())
        else:
            query_start_timestamp = int(start_time.timestamp())
            query_end_timestamp = int(end_time.timestamp())

        # get all relevant devicetrail ids from trail ids
        rows = []
        for trail_id in trail_id_list_decimals:
            rows.extend(device_trail_table.query(
                IndexName="trail-index",
                KeyConditionExpression=Key("trail_id").eq(trail_id)
            ).get("Items", []))

        # cache device-trail-devicetrail relations
        for row in rows:
            if "id" in row:
                device_trail_id = int(row["id"])
                device_trail_ids.append(device_trail_id)
                device_trail_cache[device_trail_id] = {
                    "device_id": int(row["device_id"]) if "device_id" in row else "",
                    "trail_id": int(row["trail_id"]) if "trail_id" in row else "",
                }

        # fetch relevant device logs from table in timestamp bounds
        device_log_rows = []
        if (query_end_timestamp > query_start_timestamp):
            for device_trail_id in device_trail_ids:
                rows = logs_time_table.query(
                    KeyConditionExpression=Key("device_trail_id").eq(device_trail_id) & Key("start").between(query_start_timestamp, query_end_timestamp -1)
                ).get("Items", [])
                device_log_rows.extend(rows)

        # Turn the extra starting days into a "partial" result
        if granularity in ("week", "month") and partial_start_timestamp < query_start_timestamp:
            for device_trail_id in device_trail_ids:
                start_results = device_trail_log_day_table.query(
                    KeyConditionExpression=Key("device_trail_id").eq(device_trail_id) & Key("start").between(partial_start_timestamp, query_start_timestamp - 1)
                ).get("Items", [])

                if start_results:
                    rows = {}
                    for result in start_results:
                        if result["device_trail_id"] in rows.keys():
                            rows[result["device_trail_id"]]["count"] += result["count"]
                            rows[result["device_trail_id"]]["battery"] = result["battery"]
                        else:
                            rows[result["device_trail_id"]] = {"device_trail_id": result["device_trail_id"], "start": result["start"], "count": result["count"], "battery": result["device_trail_id"]}
                    device_log_rows.extend(rows.values())

        # Turn the extra ending days into a "partial" result
        if granularity in ("week", "month") and partial_end_timestamp > query_end_timestamp:
            for device_trail_id in device_trail_ids:
                end_results = device_trail_log_day_table.query(
                    KeyConditionExpression=Key("device_trail_id").eq(device_trail_id) & Key("start").between(query_end_timestamp, partial_end_timestamp - 1)
                ).get("Items", [])

                if end_results:
                    rows = {}
                    for result in end_results:
                        if result["device_trail_id"] in rows.keys():
                            rows[result["device_trail_id"]]["count"] += result["count"]
                            rows[result["device_trail_id"]]["battery"] = result["battery"]
                        else:
                            rows[result["device_trail_id"]] = {"device_trail_id": result["device_trail_id"], "start": result["start"], "count": result["count"], "battery": result["device_trail_id"]}
                    device_log_rows.extend(rows.values())

        device_log_rows = convert_decimals(device_log_rows)

        # append rows with trail/device ids from cache
        for row in device_log_rows:
            device_trail_id = row["device_trail_id"]
            row["device_id"] = device_trail_cache[device_trail_id].get("device_id", "")
            row["trail_id"] = device_trail_cache[device_trail_id].get("trail_id", "")

        print(f"Logs successfully retrieved: [{device_log_rows[:3]}]")
        return {
            "statusCode": 200,
            "headers": cors_headers(),
            "body": json.dumps(device_log_rows)
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