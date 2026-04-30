import json

from boto3.dynamodb.conditions import Key

from helper_functions import area_table, cors_headers

def update_area(event, context):
    """
    Updates an area
    Expects: { "name": string }
    """
    try:
        print(event)
        body = event.get("body", {})
        if isinstance(body, str):
            body = json.loads(body)

        original_name = body.get("original_name")
        new_name = body.get("new_name")
        trail_ids = body.get("trail_ids")

        if original_name is None: raise ValueError("Missing required field: original_name")
        if new_name is None and trail_ids is None: raise ValueError("Missing required field: new_name or trail_ids")
        if trail_ids and not all(isinstance(id, int)  for id in trail_ids): raise ValueError("Invalid trail_ids format")

        print(f"Attempting to update with name [{original_name}")
        area_exists = area_table.query(
            KeyConditionExpression=Key("name").eq(original_name),
            Limit=1
        )["Items"]
        if not area_exists: raise ValueError(f"Cannot find area with name [{original_name}]")

        if trail_ids is None:
            trail_ids = area_exists[0]["trail_ids"]
        else:
            # Remove trails for this area from other areas
            for area in area_table.scan().get("Items", []):
                other_area_name = area.get("name")
                if original_name != other_area_name:
                    other_trail_ids = area.get("trail_ids", [])
                    if isinstance(trail_ids, list) and any(item in other_trail_ids for item in trail_ids):
                        new_trail_ids = [trail_id for trail_id in trail_ids if trail_id not in trail_ids]
                        area_table.put_item(Item={"name": other_area_name, "trail_ids": new_trail_ids})

        if new_name:
            area_table.delete_item(Key={"name": original_name})
        else:
            new_name = original_name
        area_table.put_item(Item={"name": new_name, "trail_ids": trail_ids})

        print("Successfully updated area")
        return {
            "statusCode": 200,
            "headers": cors_headers(),
            "body": json.dumps({"message": "Area updated successfully"})
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