import json

from boto3.dynamodb.conditions import Key

from helper_functions import registration_table, device_table, cors_headers, secrets_client


def edit_registration(event, context):
    """
    Edit registration entry by ID. Updates the relevant device entry and secrets manager entry accordingly.
    Registration id is mandatory. Either device name or device serial must be present. Both is also acceptable.
    Expects: { "registration_id": int, "device_name": str, "device_serial": str }
    """
    try:
        print(event)
        body = event.get("body", {})
        if isinstance(body, str):
            body = json.loads(body)

        registration_id = body.get("registration_id")
        device_name = body.get("device_name")
        device_serial = body.get("device_serial")

        if registration_id is None:
            print("Missing required field: registration_id")
            return {
                "statusCode": 400,
                "headers": cors_headers(),
                "body": json.dumps({"error": "Missing required field: registration_id"})
            }
        if device_serial is None and device_name is None:
            print("Missing required field: device_name or device_serial, one of the two must be present")
            return {
                "statusCode": 400,
                "headers": cors_headers(),
                "body": json.dumps({"error": "One of either device_name or device_serial must be present"})
            }

        print(f"Attempting to update registration entry with registration_id [{registration_id}]")

        response = registration_table.get_item(Key={"registration_id": int(registration_id)})
        item = response.get("Item")
        if not item:
            print("Registration id not found")
            return {
                "statusCode": 404,
                "headers": cors_headers(),
                "body": json.dumps({"error": "Registration not found"})
            }

        if int(item.get("date_registered")) != -1:
            print("Tried to edit active device")
            return {
                "statusCode": 400,
                "headers": cors_headers(),
                "body": json.dumps({"error": "Cannot edit a registration attached to a connected device, create a new device instead"})
            }

        device_id = item.get("device_id")
        response = device_table.get_item(Key={"id": int(device_id)})
        item = response.get("Item")

        if not item:
            print("Device id linked to provided registration entry not found")
            return {
                "statusCode": 404,
                "headers": cors_headers(),
                "body": json.dumps({"error": "Device id liked to registration entry not found"})
            }

        if device_name is not None and device_name != item.get("name"):
            old_device_name = item.get("name")

            existing = device_table.query(
                IndexName="name-index",
                KeyConditionExpression=Key("name").eq(device_name),
                Limit=1
            ).get("Items", [])

            if existing:
                raise ValueError(
                    "Device with this name already exists, delete the device first or use the existing one")

            # syntax is a bit weird here because name is a weird keyword for dynamodb, have to alias it to get it to play nice
            device_table.update_item(
                Key={"id": int(device_id)},
                UpdateExpression="SET #n = :name",
                ExpressionAttributeNames={"#n": "name"},
                ExpressionAttributeValues={":name": device_name}
            )

            # fetch old serial if serial isn't being updated too
            if device_serial is None:
                device_serial = json.loads(secrets_client.get_secret_value(SecretId=old_device_name)["SecretString"])["device_ser_no"]

            secrets_client.create_secret(
                Name=device_name,
                SecretString=json.dumps({
                    "device_name": device_name,
                    "device_ser_no": device_serial
                })
            )

            secrets_client.delete_secret(
                SecretId=old_device_name,
                ForceDeleteWithoutRecovery=True
            )
        elif device_serial is not None:
            # in this case, device_name is not changing. adjust accordingly.
            current_name = item.get("name")
            current_secret = json.loads(secrets_client.get_secret_value(SecretId=current_name)["SecretString"])
            current_secret["device_ser_no"] = device_serial
            secrets_client.put_secret_value(
                SecretId=current_name,
                SecretString=json.dumps(current_secret)
            )

        print("Successfully updated registration")
        return {
            "statusCode": 200,
            "headers": cors_headers(),
            "body": json.dumps({"message": "Registration updated successfully"})
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