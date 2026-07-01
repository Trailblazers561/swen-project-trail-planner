import json

from boto3.dynamodb.conditions import Key

from helper.helper_functions import dynamodb, device_table, device_log_table, device_trail_table, registration_table, convert_decimals, cors_headers

def get_device_metadata(event, context):
    try:
        print(event)
        multi_params = event.get("multiValueQueryStringParameters", {}) or {}

        device_id_list = multi_params.get("device_id")
        if device_id_list is not None and not all(id.isdigit() for id in device_id_list):
            raise ValueError("Invalid device_id_list format")
        device_id_list_decimals = [int(id) for id in device_id_list] if device_id_list else None

        print(f"Retrieving device metadata for device_id_list [{device_id_list_decimals}]")
        if device_id_list_decimals:
            items = []
            # split batch by 100 (that is the cap for keys in a batch)
            for hundred in (device_id_list_decimals[i:i+100] for i in range(0, len(device_id_list_decimals), 100)):
                response = dynamodb.batch_get_item(
                    RequestItems={
                        device_table.name: {"Keys": [{"id": id} for id in hundred]}
                    }
                )["Responses"].get(device_table.name, [])
                items.extend(response)
        else:
            items = device_table.scan().get("Items", [])

        print(f"Successfully found device metadata [{items[:3]}], attempting to append additional information")

        # Retrieve and add additional fields from DeviceTrail table information 
        desired_device_trail_fields = ["trail_id", "notes", "date_installed", "date_removed"]
        for item in items:
            device_trails_result = device_trail_table.query(
                KeyConditionExpression=Key("device_id").eq(item["id"]),
                ScanIndexForward=False
            ).get("Items", [])
            # Construct a list from the result with all params matching those from desired_device_trail_fields
            device_trails = [{field: device_trail[field] for field in desired_device_trail_fields if device_trail.get(field)} for device_trail in device_trails_result]
            item["trail_history"] = device_trails
            if len(device_trails_result):
                if not device_trails_result[0].get("date_removed"):
                    item["current_trail_id"] = device_trails_result[0]["trail_id"]

            registration_result = registration_table.query(
                IndexName="device-index",
                KeyConditionExpression=Key("device_id").eq(item["id"]),
                Limit=1
            ).get("Items", [])
            if registration_result:
                item["registration_id"] = registration_result[0]["registration_id"]
                item["date_registered"] = registration_result[0]["date_registered"]

            device_log_result = device_log_table.query(
                KeyConditionExpression=Key("device_id").eq(item["id"]),
                Limit=1,
                ScanIndexForward=False
            ).get("Items", [])
            if device_log_result:
                item["battery"] = device_log_result[0]["battery"]
                item["last_updated"] = device_log_result[0]["time"]

        print(f"Successfully appended device metadata [{items[:3]}]")
        return {
            "statusCode": 200,
            "headers": cors_headers(),
            "body": json.dumps(convert_decimals(items))
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