import json

from boto3.dynamodb.conditions import Key

from helper.helper_functions import area_table, cors_headers

def retire_area(event, context):
    """
    Retires an area
    Expects: { "name": string }
    """
    try:
        print(event)
        body = event.get("body", {})
        if isinstance(body, str):
            body = json.loads(body)

        name = body.get("name")

        if name is None: raise ValueError("Missing required field: name")

        print(f"Attempting to retire area with name [{name}]")
        area_exists = area_table.query(
            KeyConditionExpression=Key("name").eq(name),
            Limit=1
        )["Items"]
        if not area_exists: raise ValueError(f"Cannot find area with name [{name}]")

        area_table.put_item(Item={"name": name, "trail_ids": [], "retired": True})

        print("Successfully retired area")
        return {
            "statusCode": 200,
            "headers": cors_headers(),
            "body": json.dumps({"message": "Area retired successfully"})
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