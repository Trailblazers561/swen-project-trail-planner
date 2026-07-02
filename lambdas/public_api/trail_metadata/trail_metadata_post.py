import json
import time
from datetime import datetime
from decimal import Decimal

from helper.helper_functions import area_table, trail_table, cors_headers, get_next_trail_id

def create_trail(event, context):
    """
    Create a new trail. Auto-generates trail_id as next available ID.
    Expects: { "name": str, "area_name": str (optional), "notes": str (optional), "latitude": int (optional), "longitude": int (optional) }
    Returns: { "trail_id": int, "message": str }
    """
    try:
        print(event)
        body = event.get("body", {})
        if isinstance(body, str):
            body = json.loads(body)

        name = body.get("name")
        area_name = body.get("area_name")
        notes = body.get("notes")
        latitude = body.get("latitude")
        longitude = body.get("longitude")
        date_activated = body.get("date_activated")

        if not name:
            return {
                "statusCode": 400,
                "headers": cors_headers(),
                "body": json.dumps({"error": "Missing required field: name"})
            }

        if date_activated is None:
            date_activated = int(time.time())
        else:
            date_activated = Decimal(datetime.fromisoformat(date_activated).timestamp())

        print(f"Attempting to create trail with name [{name}], area_name [{area_name}], notes [{notes}], latitude [{latitude}], longitude [{longitude}], date_activated [{date_activated}] ")

        new_trail_id = get_next_trail_id()

        # Create trail metadata
        item = {
            "id": new_trail_id,
            "name": str(name),
            "date_activated": date_activated
        }

        if notes is not None:
            item["notes"] = notes
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
                "body": json.dumps({"error": f"Failed to create trail: {str(e)}"})
            }

        # Then add to specified area if provided
        try:
            resp = area_table.scan()
            areas = resp.get("Items", [])

            # Add to specified area if provided
            if area_name:
                area_found = False
                for area in areas:
                    if area.get("name") == area_name:
                        trail_ids = area.get("trail_ids", [])
                        if not isinstance(trail_ids, list):
                            trail_ids = []
                        if new_trail_id not in trail_ids:
                            trail_ids.append(new_trail_id)
                        area_table.put_item(Item={
                            "name": area_name,
                            "trail_ids": trail_ids
                        })
                        area_found = True
                        break

                if not area_found:
                    area_table.put_item(Item={
                        "name": area_name,
                        "trail_ids": [new_trail_id]
                    })
        except Exception as e:
            print(f"Area updated failed with exception: {e}")
            # Continue even if area update fails

        print(f"Successfully added trail with trail_id [{new_trail_id}]")
        return {
            "statusCode": 200,
            "headers": cors_headers(),
            "body": json.dumps({
                "message": "Trail created successfully",
                "trail_id": new_trail_id
            })
        }
    except Exception as e:
        print(e)
        return {
            "statusCode": 500,
            "headers": cors_headers(),
            "body": json.dumps({"error": f"Internal server error: {str(e)}"})
        }