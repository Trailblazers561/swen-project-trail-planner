import json

from boto3.dynamodb.conditions import Key

from helper.helper_functions import area_table, cors_headers

def create_area(event, context):
    """
    Creates an area
    Expects: { "name": string }
    """
    try:
        print(event)
        body = event.get("body", {})
        if isinstance(body, str):
            body = json.loads(body)

        name = body.get("name")
        trail_ids = body.get("trail_ids")

        if name is None: raise ValueError("Missing required field: name")
        if trail_ids is None: trail_ids = []
        if trail_ids and not all(isinstance(id, int) for id in trail_ids): raise ValueError("Invalid trail_ids format")

        print(f"Attempting to create area with name [{name}]")
        area_exists = area_table.query(
            KeyConditionExpression=Key("name").eq(name),
            Limit=1
        )["Items"]
        if area_exists: raise ValueError(f"Already found area with name [{name}]")

        if trail_ids:
            # Remove trails for this area from other areas
            for area in area_table.scan().get("Items", []):
                other_area_name = area.get("name")
                if name != other_area_name:
                    other_trail_ids = area.get("trail_ids", [])
                    if isinstance(trail_ids, list) and any(item in other_trail_ids for item in trail_ids):
                        new_trail_ids = [trail_id for trail_id in other_trail_ids if trail_id not in trail_ids]
                        area_table.put_item(Item={"name": other_area_name, "trail_ids": new_trail_ids})

        area_table.put_item(Item={"name": name, "trail_ids": trail_ids})

        print("Successfully created area")
        return {
            "statusCode": 200,
            "headers": cors_headers(),
            "body": json.dumps({"message": "Area created successfully"})
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