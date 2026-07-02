import json
from decimal import Decimal

from helper.helper_functions import area_table, trail_table, cors_headers

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

        if trail_id is None: raise ValueError("Missing required field: trail_id")
        if not isinstance(trail_id, int): raise ValueError("Invalid trail_id format")
        if name and not isinstance(name, str): raise ValueError("Invalid name format")
        if area_name and not isinstance(area_name, str): raise ValueError("Invalid area_name format")
        if notes and not isinstance(notes, str): raise ValueError("Invalid notes format")
        if latitude and not isinstance(latitude, (float, int, Decimal)): raise ValueError("Invalid latitude format")
        if longitude and not isinstance(longitude, (float, int, Decimal)): raise ValueError("Invalid longitude format")

        print(f"Attempting to update trail with trail_id [{trail_id}] to name [{name}] and area_name [{area_name}] and notes [{notes}] and latitude [{latitude}] and longitude [{longitude}]")

        # Update trail metadata
        update_expressions = []
        expression_names = {}
        expression_values = {}
        if name is not None:
            update_expressions.append(" #name = :name")
            expression_names["#name"] = "name"
            expression_values[":name"] = name
        if notes is not None:
            update_expressions.append(" notes = :notes")
            expression_values[":notes"] = notes
        if latitude is not None:
            update_expressions.append(" latitude = :latitude")
            expression_values[":latitude"] = Decimal(str(latitude)) if latitude else 0
        if longitude is not None:
            update_expressions.append(" longitude = :longitude")
            expression_values[":longitude"] = Decimal(str(longitude)) if longitude else 0

        try:
            if update_expressions:
                trail_table.update_item(
                    Key={"id": trail_id},
                    UpdateExpression=f"SET {', '.join(update_expressions)} REMOVE date_retired",
                    ExpressionAttributeNames=expression_names,
                    ExpressionAttributeValues=expression_values
                )
            else:
                trail_table.update_item(
                    Key={"id": trail_id},
                    UpdateExpression="REMOVE date_retired"
                )
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
                    if area.get("name") == area_name:
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

        print("Successfully updated trail metadata")
        return {
            "statusCode": 200,
            "headers": cors_headers(),
            "body": json.dumps({"message": "Trail metadata updated successfully"})
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