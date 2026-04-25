import json

from boto3.dynamodb.conditions import Key

from helper_functions import trail_group_table, cors_headers

def delete_trail_group(event, context):
    """
    Deletes a trail group
    Expects: { "name": string }
    """
    try:
        print(event)
        body = event.get("body", {})
        if isinstance(body, str):
            body = json.loads(body)

        name = body.get("group_name")

        if name is None: raise ValueError("Missing required field: group_name")

        print(f"Attempting to delete trail group with name [{name}")
        trail_group_exists = trail_group_table.query(
            KeyConditionExpression=Key("name").eq(name),
            Limit=1
        )["Items"]
        if not trail_group_exists: raise ValueError(f"Cannot find trail_group with name [{name}]")

        trail_group_table.delete_item(Key={"name": name})

        print("Successfully deleted trail group")
        return {
            "statusCode": 200,
            "headers": cors_headers(),
            "body": json.dumps({"message": "Trail group deleted successfully"})
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