import json

from boto3.dynamodb.conditions import Attr

from helper_functions import dynamodb, trail_table, convert_decimals, cors_headers

def get_trail_metadata(event, context):
    try:
        print(event)
        multi_params = event.get("multiValueQueryStringParameters", {}) or {}

        trail_id_list = multi_params.get("trail_id")
        if trail_id_list is not None and not all(id.isdigit() for id in trail_id_list):
            raise ValueError("Invalid trail_id_list format")
        trail_id_list_decimals = [int(id) for id in trail_id_list] if trail_id_list else None

        print(f"Retrieving trail metadata for trail_id_list [{trail_id_list_decimals}]")
        if trail_id_list_decimals:
            items = []
            # split batch by 100 (that is the cap for keys in a batch)
            for hundred in (trail_id_list_decimals[i:i+100] for i in range(0, len(trail_id_list_decimals), 100)):
                response = dynamodb.batch_get_item(
                    RequestItems={
                        trail_table.name: {"Keys": [{"id": id} for id in hundred]}
                    }
                )["Responses"].get(trail_table.name, [])
                items.extend(response)
        else:   
            items = trail_table.scan(FilterExpression=Attr("date_retired").not_exists()).get("Items", [])

        print(f"Successfully found trail metadata [{items[:3]}]")
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