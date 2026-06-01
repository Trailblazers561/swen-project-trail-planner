import json

from helper_functions import dynamodb, area_table, convert_decimals, cors_headers

def get_areas(event, context):
    try:
        print(event)
        multi_params = event.get("multiValueQueryStringParameters", {}) or {}

        area_list = multi_params.get("name")

        print(f"Retrieving areas for area_list [{area_list}]")
        if area_list:
            items = []
            # split batch by 100 (that is the cap for keys in a batch)
            for hundred in (area_list[i:i+100] for i in range(0, len(area_list), 100)):
                response = dynamodb.batch_get_item(
                    RequestItems={
                        area_table.name: {"Keys": [{"name": name} for name in hundred]}
                    }
                )["Responses"].get(area_table.name, [])
                items.extend(response)
        else:   
            items = area_table.scan().get("Items", [])

        print(f"Successfully found areas [{items[:3]}]")
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