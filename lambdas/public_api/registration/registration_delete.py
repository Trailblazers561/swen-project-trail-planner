import json

from helper.helper_functions import registration_table, device_table, cors_headers, secrets_client, device_secret_id


def delete_registration(event, context):
    """
    Delete registration entry by ID. Deletes the associated device entry stub and the secrets manager value.
    Expects: { "registration_id": int }
    """
    try:
        print(event)
        body = event.get("body", {})
        if isinstance(body, str):
            body = json.loads(body)

        registration_id = body.get("registration_id")

        if registration_id is None:
            print("Missing required field: registration_id")
            raise ValueError("Missing required field: registration_id")

        print(f"Attempting to delete registration entry with registration_id [{registration_id}]")

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
            print("Tried to delete active device")
            raise ValueError("Cannot delete a registration attached to a connected device, try retiring instead")

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

        device_name = item.get("name")

        secrets_client.delete_secret(
            SecretId=device_secret_id(device_name),
            ForceDeleteWithoutRecovery=True
        )
        device_table.delete_item(Key={"id": int(device_id)})
        registration_table.delete_item(Key={"registration_id": int(registration_id)})

        print("Successfully deleted registration")
        return {
            "statusCode": 200,
            "headers": cors_headers(),
            "body": json.dumps({"message": "Registration deleted successfully"})
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