import json
from decimal import Decimal

from boto3.dynamodb.conditions import Key

from helper_functions import convert_decimals, cors_headers, device_log_table

def get_device_management(event, context):
    try:
        print(event)
        single_params = event.get("queryStringParameters", {}) or {}
        multi_params = event.get("multiValueQueryStringParameters", {}) or {}

        limit = single_params.get("limit")
        device_id_list = multi_params.get('device_id')

        if device_id_list is None: raise ValueError("Missing required field(s): device_id")
        if not all(id.isdigit() for id in device_id_list):
            raise ValueError("Invalid device_id_list format")

        device_id_list_decimals = [Decimal(id) for id in device_id_list]

        if limit is not None and not limit.isdigit():
            raise ValueError("Invalid limit format")
        limit = 5 if limit is None else int(limit)

        print(f"Retrieving device management information for device_id_list [{device_id_list}]")
        items = []
        for device_id in device_id_list_decimals:
            if limit == -1:
                response = device_log_table.query(KeyConditionExpression=Key("device_id").eq(device_id)).get("Items", [])
            else:
                response = device_log_table.query(KeyConditionExpression=Key("device_id").eq(device_id), Limit=limit).get("Items", [])
            items.extend(response)

        print(f"Successfully retrieved device logs [{items[:3]}]")
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
            "body": json.dumps({"error": str(e)})
        }
    except Exception as e:
        print(e)
        return {
            "statusCode": 500,
            "headers": cors_headers(),
            "body": json.dumps({"error": f"Internal server error: {str(e)}"})
        }
