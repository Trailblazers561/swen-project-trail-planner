import json
from helper_functions import convert_decimals, cors_headers, dynamodb, device_log_table

def get_device_management(event, context):
    try:
        print(event)
        multi_params = event.get("multiValueQueryStringParameters", {}) or {}

        device_id_list = multi_params.get('device_id')
        if device_id_list is not None and not all(id.isdigit() for id in device_id_list):
            raise ValueError("Invalid device_id_list format")
        
        print(f"Retrieving device management information for device_id_list [{device_id_list}]")
        if device_id_list:
            items = []
            # split batch by 100 (that is the cap for keys in a batch)
            for hundred in (device_id_list[i:i+100] for i in range(0, len(device_id_list), 100)):
                response = dynamodb.batch_get_item(
                    RequestItems={
                        device_log_table.name: {"Keys": [{"id": int(id)} for id in hundred]}
                    }
                )["Responses"].get(device_log_table.name, [])
                items.extend(response)
        else:
            items = device_log_table.scan().get("Items", [])

        print(f"Successfully retrieved device metadata [{items[:3]}]")
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