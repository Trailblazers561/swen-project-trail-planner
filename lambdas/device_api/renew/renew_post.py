from datetime import datetime, timezone, timedelta

import requests
import json
import time

from cryptography import x509
from boto3.dynamodb.conditions import Key
from helper.helper_functions import device_table, registration_table, cors_headers, secrets_client, CA_URL, get_root_ca_cert, check_ca_health, gen_one_time_token


def renew_certificate(event, context):
    try:
        print("Renewing device...")
        print("Checking CA status...")
        healthCheck = check_ca_health()
        if healthCheck["status"] != "ok":
            raise ValueError("Server health check failed")
        print(healthCheck)
        body = json.loads(event.get("body") or "{}")

        device_name = body.get("device_name")
        if not device_name:
            raise ValueError("Device name not provided")

        # device name provided not in table? drop packet
        response = device_table.query(
            IndexName="name-index",
            KeyConditionExpression=Key("name").eq(str(device_name)),
        )
        items = response.get("Items", [])

        if not items:
            raise ValueError("Device name not found, try registering the device before connecting")
        item = items[0]

        reg_response = registration_table.query(
            IndexName="device-index",
            KeyConditionExpression=Key("device_id").eq(int(item.get("id")))
        )
        reg_items = reg_response.get("Items", [])

        if not reg_items:
            raise ValueError("Device not found in registration, try registering the device before connecting")

        # Reject blocked devices
        if item.get("is_blocked"):
            return {
                "statusCode": 403,
                "headers": cors_headers(),
                "body": json.dumps({"error": "Device is blocked. Renewal rejected."})
            }

        # Reject archived devices
        if item.get("is_archived"):
            return {
                "statusCode": 403,
                "headers": cors_headers(),
                "body": json.dumps({"error": "Device is archived. Renewal rejected."})
            }

        device_secrets = json.loads(secrets_client.get_secret_value(SecretId=str(device_name))["SecretString"])
        device_serial = device_secrets["device_ser_no"]
        csr = device_secrets["csr"]

        if not csr:
            raise ValueError("No csr for the device present, try registering the device before attempting a renewal")

        # if the device is in device table, serial should be there guaranteed, this shouldn't fire
        if not device_serial:
            raise ValueError("Device Serial not found, ensure the device is properly registered before connecting")

        one_time_token = gen_one_time_token(csr, device_name)

        # cert exp date(max, min and default configured in step-ca setup in the ec2 file)
        # set to default for now(change later)
        not_after = (datetime.now(timezone.utc) + timedelta(hours=720)).strftime("%Y-%m-%dT%H:%M:%SZ")

        response = requests.post(
            f"{CA_URL}/1.0/sign",
            json={
                "csr": csr,
                "ott": one_time_token,
                "notAfter": not_after,
            },
            verify=get_root_ca_cert()
        )

        response.raise_for_status()

        # successful certificate request at this point
        data = response.json()
        certificate = {"certificate": data["crt"]}

        cert = x509.load_pem_x509_certificate(data["crt"].encode())
        time_now = int(time.time())
        time_to_live = int(cert.not_valid_after_utc.timestamp()) - time_now

        # registration table functionality
        registration_table.update_item(
            Key={"registration_id": reg_items[0]["registration_id"]},
            UpdateExpression="SET date_registered = if_not_exists(date_registered, :dr), cert_time_to_live = :tl",
            ExpressionAttributeValues={
                ":dr": time_now,
                ":tl": time_to_live
            }
        )

        return {
            "statusCode": 200,
            "headers": cors_headers(),
            "body": json.dumps(certificate)
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