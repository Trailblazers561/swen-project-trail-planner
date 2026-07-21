import hashlib
import hmac
import json
import time
from datetime import datetime, timezone, timedelta

from botocore.exceptions import ClientError
from cryptography import x509
import requests
from boto3.dynamodb.conditions import Key
from helper.helper_functions import device_table, registration_table, cors_headers, secrets_client, CA_URL, \
    get_root_ca_cert, check_ca_health, gen_one_time_token, device_secret_id, device_log_table

TIMESTAMP_WINDOW = 120  # 2 min buffer from packet send time to parse time


def register_device(event, context):
    """
    Main register device function. Takes in a packet of {{device_name, timestamp, csr}, hash}. All fields are required.
    device_name is the name of the device to register that should match with the device table entry/secrets manager key.
    timestamp is the device's time that it sends the value at. The timestamp must be within 2 minutes of the time it gets
    parsed by the server. The certificate signing request is sent to the certificate authority to generate a new certificate for.
    The hash is the object comprised of the previous 3 values, hashed against the device serial number. This is calcualted
    and checked locally in the function.

    If any of the above do not match(any values not present, device name not in device table, timestamp out of accepted range,
    hash doesn't match), the packet is dropped. If the device is blocked or archived, packet is dropped. Once the validation
    is complete, a one-time-token is generated, and the csr is sent to the certificate authority with the token attached.

    The CA will return a certificate if the certificate signing request goes through properly.

    Once successful, the CSR will be stored in secrets manager for later renewals and the registration table entries will
    be updated with the time to live and date registered.
    :param event:
    :param context:
    :return: Certificate
    """
    try:
        print("Registering device...")
        print("Checking CA status...")
        healthCheck = check_ca_health()
        if healthCheck["status"] != "ok":
            raise ValueError("Server health check failed")
        print(healthCheck)
        body = json.loads(event.get("body") or "{}")

        device_name = body.get("device_name")
        if not device_name:
            raise ValueError("Device name not provided")
        timestamp = body.get("timestamp")
        if not timestamp:
            raise ValueError("Timestamp not provided")
        csr = body.get("csr")
        if not csr:
            raise ValueError("CSR not provided")
        provided_hmac = body.get("hmac")
        if not provided_hmac:
            raise ValueError("HMAC hash not provided")

        # time between submission too late? reject packet
        time_now = int(time.time())
        time_delta = abs(time_now - int(timestamp))
        if time_delta > TIMESTAMP_WINDOW:
            raise ValueError(
                f"Packet timestamp outside accepted window of {TIMESTAMP_WINDOW}, ensure device connectivity is working properly")

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
                "body": json.dumps({"error": "Device is blocked. Registration rejected."})
            }

        # Reject archived devices
        if item.get("is_archived"):
            return {
                "statusCode": 403,
                "headers": cors_headers(),
                "body": json.dumps({"error": "Device is archived. Registration rejected."})
            }

        device_secret = json.loads(secrets_client.get_secret_value(SecretId=device_secret_id(str(device_name)))["SecretString"])

        device_serial = device_secret.get("device_ser_no")

        # if the device is in device table, serial should be there guaranteed, this shouldn't fire
        if not device_serial:
            raise ValueError("Device Serial not found, ensure the device is properly registered before connecting")

        # provided hash signature doesnt match self-computed hash? drop packet
        plaintext_string = f"{device_name}:{timestamp}:{csr}".encode()
        encoding = hmac.new(device_serial.encode(), plaintext_string, hashlib.sha512).hexdigest()
        if not hmac.compare_digest(provided_hmac, encoding):
            raise ValueError("HMAC hash does not match, ensure device serial number is accurate")

        # at this point we're sure the sender is the actual device and not someone spoofing it.
        # time to fire off the certificate
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

        # upload csr for reuse later
        device_secret["csr"] = csr
        secrets_client.update_secret(SecretId=device_secret_id(str(device_name)), SecretString=json.dumps(device_secret))

        cert = x509.load_pem_x509_certificate(data["crt"].encode())
        time_now = int(time.time())
        time_to_live = int(cert.not_valid_after_utc.timestamp()) - time_now

        # registration table functionality
        registration_table.update_item(
            Key={"registration_id": reg_items[0]["registration_id"]},
            UpdateExpression="SET date_cert_issued = :dc, cert_time_to_live = :tl",
            ExpressionAttributeValues={
                ":dc": time_now,
                ":tl": time_to_live
            }
        )

        try:
            registration_table.update_item(
                Key={"registration_id": reg_items[0]["registration_id"]},
                UpdateExpression="SET date_registered = :dr",
                ConditionExpression="date_registered = :presetValue",
                ExpressionAttributeValues={
                    ":dr": time_now,
                    ":presetValue": -1
                }
            )
        except ClientError as e:
            if e.response["Error"]["Code"] != "ConditionalCheckFailedException":
                # that error was relevant, raise it
                raise
            else:
                # device already registered, ignore and move on
                pass

        device_log_table.put_item(Item={
            "device_id": int(item.get("id")),
            "time": int(str(datetime.now().timestamp())),
            "log_type": "device_certificate_registration",
        })

        return {
            "statusCode": 200,
            "headers": cors_headers(),
            "body": json.dumps(certificate)
        }

    except ValueError as exception:
        print(exception)
        return {
            "statusCode": 400,
            "headers": cors_headers(),
            "body": json.dumps({"error": f"{str(exception)}"})
        }
    except Exception as exception:
        print(exception)
        return {
            "statusCode": 500,
            "headers": cors_headers(),
            "body": json.dumps({"error": f"Internal server error: {str(exception)}"})
        }
