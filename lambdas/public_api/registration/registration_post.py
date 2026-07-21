import json

from boto3.dynamodb.conditions import Key

from helper.helper_functions import registration_table, device_table, cors_headers, get_next_device_id, secrets_client, \
    get_next_registration_id, device_secret_id


def pre_register_device(event, context):
    """
    Creates a device table entry and a registration table entry. Stores device_serial in aws secret manager keyed to
    device_name. Must be done to establish the proper device existence and secure/validate it before actually performing
    device registration and trusting data from it.
    Expects: { "device_name": str, "device_serial": str }
    """
    try:
        print(event)
        body = event.get("body", {})
        if isinstance(body, str):
            body = json.loads(body)

        device_name = body.get("device_name")
        device_serial = body.get("device_serial")

        if device_name is None:
            raise ValueError("Missing required field: device_name")
        if device_serial is None:
            raise ValueError("Missing required field: device_serial")

        # make sure a device with our given name doesn't already exist. not a 100% guaranteed check as a user
        # could screw up the name, but this does a reasonably good job at it. if it does we'll pair with that instead.
        existing = device_table.query(
            IndexName="name-index",
            KeyConditionExpression=Key("name").eq(device_name),
            Limit=1
        ).get("Items", [])

        if existing:
            raise ValueError("Device with this name already exists, delete the device first or use the existing one")
        else:
            # normal operation
            new_device_id = get_next_device_id()

            secrets_client.create_secret(
                Name=device_secret_id(device_name),
                SecretString=json.dumps({
                    "device_name": device_name,
                    "device_ser_no": device_serial
                })
            )

            device_table.put_item(Item={
                "id": new_device_id,
                "name": device_name,
                "is_blocked": False,
                "is_archived": False,
            })

            new_registration_id = get_next_registration_id()

            registration_table.put_item(Item={
                "registration_id": new_registration_id,
                "device_id": new_device_id,
                "date_registered": -1,
            })

            return {
                "statusCode": 200,
                "headers": cors_headers(),
                "body": json.dumps({
                    "message": "Device registered successfully",
                    "device_id": new_device_id,
                    "registration_id": new_registration_id
                })
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
