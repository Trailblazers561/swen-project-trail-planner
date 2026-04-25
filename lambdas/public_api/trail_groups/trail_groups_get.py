import json

from helper_functions import dynamodb, trail_group_table, convert_decimals, cors_headers

def get_trail_group_metadata(event, context):
    try:
        print(event)
        multi_params = event.get("multiValueQueryStringParameters", {}) or {}

        trail_group_list = multi_params.get("trail_group")

        print(f"Retrieving trail groups for trail_group_list [{trail_group_list}]")
        if trail_group_list:
            items = []
            # split batch by 100 (that is the cap for keys in a batch)
            for hundred in (trail_group_list[i:i+100] for i in range(0, len(trail_group_list), 100)):
                response = dynamodb.batch_get_item(
                    RequestItems={
                        trail_group_table.name: {"Keys": [{"name": name} for name in hundred]}
                    }
                )["Responses"].get(trail_group_table.name, [])
                items.extend(response)
        else:   
            items = trail_group_table.scan().get("Items", [])

        print(f"Successfully found trail groups [{items[:3]}]")
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