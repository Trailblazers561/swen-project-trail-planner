import json
import time
from datetime import datetime
from decimal import Decimal

from boto3.dynamodb.conditions import Key

from helper_functions import trail_table, device_trail_table, trail_group_table, cors_headers

def retire_trail(event, context):
    """
    Retires a trail and all associated data.
    Deletes:
    - Trail from all trail groups
    - Updates devices_trail date removed to given date
    - Updates trail date retired to given date
    Expects: { "trail_id": int, date_retired: str (ISO Date, optional) }
    """
    try:
        print(event)
        body = event.get("body", {})
        if isinstance(body, str):
            body = json.loads(body)

        trail_id = body.get("trail_id")
        date_retired = body.get("date_retired")

        if trail_id is None:
            print("Missing required field: trial_id")
            return {
                "statusCode": 400,
                "headers": cors_headers(),
                "body": json.dumps({"error": "Missing required field: trail_id"})
            }

        try:
            trail_id = int(trail_id)
        except (ValueError, TypeError):
            print("Failed to delete trail due to invalid trail_id format")
            return {
                "statusCode": 400,
                "headers": cors_headers(),
                "body": json.dumps({"error": "Invalid trail_id format"})
            }

        if date_retired is None:
            date_retired = int(time.time())
        else:
            date_retired = Decimal(datetime.fromisoformat(date_retired).timestamp())

        print(f"Attempting to retire trail with trail_id [{trail_id}] with date [{date_retired}]")

        # get all relevant devicetrail ids for this trail
        response = device_trail_table.query(
            IndexName="trail-index",
            KeyConditionExpression=Key("trail_id").eq(trail_id)
        )
        device_trail_items = response.get("Items", [])

        for device_trail_item in device_trail_items:
            if not device_trail_item["date_removed"]:
                device_trail_table.update_item(
                    Key={"device_id": device_trail_item["device_id"], "date_installed": device_trail_item["date_installed"]},
                    UpdateExpression="SET date_removed = :date_removed",
                    ExpressionAttributeValues={":date_removed": date_retired}
                )

        # Remove trail from all trail groups
        try:
            resp = trail_group_table.scan()
            groups = resp.get("Items", [])

            for group in groups:
                trail_ids = group.get("trail_ids", [])
                if isinstance(trail_ids, list) and trail_id in trail_ids:
                    trail_ids = [tid for tid in trail_ids if tid != trail_id]
                    trail_group_table.put_item(Item={
                        "name": group.get("name"),
                        "trail_ids": trail_ids
                    })
        except Exception as e:
            # Log error but continue
            print(f"Error removing trail from groups: {str(e)}")

        try:
            trail_table.update_item(
                Key={"id": trail_id},
                UpdateExpression="SET date_retired = :date_retired",
                ExpressionAttributeValues={":date_retired": date_retired}
            )
        except Exception as e:
            print(e)
            return {
                "statusCode": 500,
                "headers": cors_headers(),
                "body": json.dumps({"error": f"Failed to retire trail: {str(e)}"})
            }

        print("Successfully retired trail")
        return {
            "statusCode": 200,
            "headers": cors_headers(),
            "body": json.dumps({"message": "Trail and all associated data retired successfully"})
        }
    except Exception as e:
        print(e)
        return {
            "statusCode": 500,
            "headers": cors_headers(),
            "body": json.dumps({"error": f"Internal server error: {str(e)}"})
        }