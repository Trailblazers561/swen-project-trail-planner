import json
from decimal import Decimal

from helper_functions import area_table, trail_table, cors_headers

def update_trail_metadata(event, context):
    """
    Update trail metadata (trail name, area).
    Expects: { "trail_id": int, "name": str, "area_name": str, "notes": str, "latitude": float, "longitude": float }
    """
    try:
        print(event)
        body = event.get("body", {})
        if isinstance(body, str):
            body = json.loads(body)

        trail_id = body.get("trail_id")
        name = body.get("name")
        area_name = body.get("area_name")
        notes = body.get("notes")
        latitude = body.get("latitude")
        longitude = body.get("longitude")

        if trail_id is None:
            return {
                "statusCode": 400,
                "headers": cors_headers(),
                "body": json.dumps({"error": "Missing required field: trail_id"})
            }

        print(f"Attempting to update trail with trail_id [{trail_id}] to name [{name}] and area_name [{area_name}] and notes [{notes}] and latitude [{latitude}] and longitude [{longitude}]")

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

        # Update areas if area is provided (and not empty string)
        if area_name is not None and area_name != "":
            try:
                # Get current areas
                resp = area_table.scan()
                areas = resp.get("Items", [])

                # First, remove trail_id from all other areas
                for area in areas:
                    other_area_name = area.get("name")
                    if area_name != other_area_name:
                        trail_ids = area.get("trail_ids", [])
                        if isinstance(trail_ids, list) and trail_id in trail_ids:
                            trail_ids = [tid for tid in trail_ids if tid != trail_id]
                            area_table.put_item(Item={
                                "name": other_area_name,
                                "trail_ids": trail_ids
                            })

                # Find the target area and add trail_id to it
                area_found = False
                for area in areas:
                    if area.get("name") == area:
                        trail_ids = area.get("trail_ids", [])
                        if not isinstance(trail_ids, list):
                            trail_ids = []
                        if trail_id not in trail_ids:
                            trail_ids.append(trail_id)
                        area_table.put_item(Item={
                            "name": area_name,
                            "trail_ids": trail_ids
                        })
                        area_found = True
                        break

                    # If area doesn't exist, create it
                    if not area_found:
                        area_table.put_item(Item={
                            "name": area_name,
                            "trail_ids": [trail_id]
                        })
            except Exception as e:
                print(f"Failed updating area with exception: {e}")
                # Continue even if area update fails
                pass
        else:
            # If area is None (empty string), remove it from all areas
            # This handles the case when removing a trail from a specific area
            try:
                resp = area_table.scan()
                areas = resp.get("Items", [])

                # Remove from all areas
                for area in areas:
                    other_area_name = area.get("name")
                    trail_ids = area.get("trail_ids", [])
                    if isinstance(trail_ids, list) and trail_id in trail_ids:
                        trail_ids = [tid for tid in trail_ids if tid != trail_id]
                        area_table.put_item(Item={
                            "name": other_area_name,
                            "trail_ids": trail_ids
                        })

            except Exception as e:
                print(f"Failed removing trail areas with exception: {e}")
                # Continue even if area update fails
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