import json
from decimal import Decimal

from helper_functions import trail_table, trail_group_table, cors_headers

def update_trail_metadata(event, context):
    """
    Update trail metadata (trail name, trail group).
    Expects: { "trail_id": int, "name": str, "area": str, "notes": str, "latitude": float, "longitude": float }
    """
    try:
        print(event)
        body = event.get("body", {})
        if isinstance(body, str):
            body = json.loads(body)

        trail_id = body.get("trail_id")
        name = body.get("name")
        area = body.get("area")
        notes = body.get("notes")
        latitude = body.get("latitude")
        longitude = body.get("longitude")

        if trail_id is None:
            return {
                "statusCode": 400,
                "headers": cors_headers(),
                "body": json.dumps({"error": "Missing required field: trail_id"})
            }

        print(f"Attempting to update trail with trail_id [{trail_id}] to name [{name}] and area [{area}] and notes [{notes}] and latitude [{latitude}] and longitude [{longitude}]")

        try:
            trail_id = int(trail_id)
        except (ValueError, TypeError):
            return {
                "statusCode": 400,
                "headers": cors_headers(),
                "body": json.dumps({"error": "Invalid trail_id format"})
            }

        # Update trail metadata
        item = {"id": trail_id}
        if name is not None:
            item["name"] = str(name)
        if notes is not None:
            item["notes"] = str(notes)
        if latitude is not None:
            item["latitude"] = Decimal(str(latitude))
        if longitude is not None:
            item["longitude"] = Decimal(str(longitude))

        try:
            trail_table.put_item(Item=item)
        except Exception as e:
            print(e)
            return {
                "statusCode": 500,
                "headers": cors_headers(),
                "body": json.dumps({"error": f"Failed to update trail metadata: {str(e)}"})
            }

        # Update trail groups if area is provided (and not empty string)
        if area is not None and area != "":
            try:
                # Get current trail groups
                resp = trail_group_table.scan()
                groups = resp.get("Items", [])

                # First, remove trail_id from all other groups
                for group in groups:
                    group_name = group.get("name")
                    if group_name != area:
                        trail_ids = group.get("trail_ids", [])
                        if isinstance(trail_ids, list) and trail_id in trail_ids:
                            trail_ids = [tid for tid in trail_ids if tid != trail_id]
                            trail_group_table.put_item(Item={
                                "name": group_name,
                                "trail_ids": trail_ids
                            })

                # Find the target group and add trail_id to it
                group_found = False
                for group in groups:
                    if group.get("name") == area:
                        trail_ids = group.get("trail_ids", [])
                        if not isinstance(trail_ids, list):
                            trail_ids = []
                        if trail_id not in trail_ids:
                            trail_ids.append(trail_id)
                        trail_group_table.put_item(Item={
                            "name": area,
                            "trail_ids": trail_ids
                        })
                        group_found = True
                        break

                    # If group doesn't exist, create it
                    if not group_found:
                        trail_group_table.put_item(Item={
                            "name": area,
                            "trail_ids": [trail_id]
                        })
            except Exception as e:
                print(f"Failed updating trail group with exception: {e}")
                # Continue even if trail group update fails
                pass
        else:
            # If area is None (empty string), remove it from all groups
            # This handles the case when removing a trail from a specific group
            try:
                resp = trail_group_table.scan()
                groups = resp.get("Items", [])

                # Remove from all groups
                for group in groups:
                    group_name = group.get("name")
                    trail_ids = group.get("trail_ids", [])
                    if isinstance(trail_ids, list) and trail_id in trail_ids:
                        trail_ids = [tid for tid in trail_ids if tid != trail_id]
                        trail_group_table.put_item(Item={
                            "name": group_name,
                            "trail_ids": trail_ids
                        })

            except Exception as e:
                print(f"Failed updating trail group with exception: {e}")
                # Continue even if trail group update fails
                pass

        print("Successfully updated trail metadata")
        return {
            "statusCode": 200,
            "headers": cors_headers(),
            "body": json.dumps({"message": "Trail metadata updated successfully"})
        }
    except Exception as e:
        print(e)
        return {
            "statusCode": 500,
            "headers": cors_headers(),
            "body": json.dumps({"error": f"Internal server error: {str(e)}"})
        }