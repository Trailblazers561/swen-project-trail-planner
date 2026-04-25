import json
from decimal import Decimal

from helper_functions import trail_table, trail_group_table, cors_headers

def update_trail_metadata(event, context):
    """
    Update trail metadata (trail name, trail group).
    Expects: { "trail_id": int, "trail_name": str, "trail_group": str, "trail_notes": str, "trail_latitude": float, "trail_longitude": float }
    """
    try:
        print(event)
        body = event.get("body", {})
        if isinstance(body, str):
            body = json.loads(body)

        trail_id = body.get("trail_id")
        trail_name = body.get("trail_name")
        trail_group = body.get("trail_group")
        trail_notes = body.get("trail_notes")
        trail_lat = body.get("trail_latitude")
        trail_lon = body.get("trail_longitude")

        if trail_id is None:
            return {
                "statusCode": 400,
                "headers": cors_headers(),
                "body": json.dumps({"error": "Missing required field: trail_id"})
            }

        print(f"Attempting to update trail with trail_id [{trail_id}] to trail_name [{trail_name}] and trail_group [{trail_group}] and notes [{trail_notes}] and latitude [{trail_lat}] and longitude [{trail_lon}]")

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
        if trail_name is not None:
            item["name"] = str(trail_name)
        if trail_notes is not None:
            item["notes"] = str(trail_notes)
        if trail_lat is not None:
            item["latitude"] = Decimal(str(trail_lat))
        if trail_lon is not None:
            item["longitude"] = Decimal(str(trail_lon))

        try:
            trail_table.put_item(Item=item)
        except Exception as e:
            print(e)
            return {
                "statusCode": 500,
                "headers": cors_headers(),
                "body": json.dumps({"error": f"Failed to update trail metadata: {str(e)}"})
            }

        # Update trail groups if trail_group is provided (and not empty string)
        if trail_group is not None and trail_group != "":
            try:
                # Get current trail groups
                resp = trail_group_table.scan()
                groups = resp.get("Items", [])

                # First, remove trail_id from all other groups
                for group in groups:
                    group_name = group.get("name")
                    if group_name != trail_group:
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
                    if group.get("name") == trail_group:
                        trail_ids = group.get("trail_ids", [])
                        if not isinstance(trail_ids, list):
                            trail_ids = []
                        if trail_id not in trail_ids:
                            trail_ids.append(trail_id)
                        trail_group_table.put_item(Item={
                            "name": trail_group,
                            "trail_ids": trail_ids
                        })
                        group_found = True
                        break

                    # If group doesn't exist, create it
                    if not group_found:
                        trail_group_table.put_item(Item={
                            "name": trail_group,
                            "trail_ids": [trail_id]
                        })
            except Exception as e:
                print(f"Failed updating trail group with exception: {e}")
                # Continue even if trail group update fails
                pass
        else:
            # If trail_group is None (empty string), remove it from all groups
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