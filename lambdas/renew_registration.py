import os
from datetime import datetime, timezone, timedelta

import boto3
import requests
import base64
import json
import time
import hashlib
import uuid

from cryptography import x509
from jwcrypto import jwk, jwt
from boto3.dynamodb.conditions import Key
from cryptography.hazmat.primitives.serialization import Encoding
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC
from cryptography.hazmat.primitives.keywrap import aes_key_unwrap
from cryptography.hazmat.primitives.ciphers.aead import AESGCM
from cryptography.x509 import load_pem_x509_csr
from cryptography.hazmat.backends import default_backend


CA_URL = os.environ.get("CERTIFICATE_AUTHORITY_URL")
CA_CERT_PATH = "tmp/root_ca.crt"

dynamodb = boto3.resource('dynamodb')
secrets_client = boto3.client("secretsmanager")
registration_table = dynamodb.Table(os.environ.get("REGISTRATION_TABLE", "local_Registration"))
device_table = dynamodb.Table(os.environ.get("DEVICE_TABLE", "local_Device"))


def cors_headers():
    return {
        "Access-Control-Allow-Origin": "*",
        "Access-Control-Allow-Methods": "PUT",
        "Access-Control-Allow-Headers": "Content-Type,Authorization"
    }


def get_root_ca_cert():
    """
    Get the root ca certificate from secrets manager, and saves it locally at
    tmp/root_ca.crt
    :return: path to the root ca file
    """
    if not os.path.exists(CA_CERT_PATH):
        os.makedirs("tmp", exist_ok=True)
        sm = boto3.client("secretsmanager")
        response = sm.get_secret_value(SecretId="cert-auth/root-ca-cert")
        with open(CA_CERT_PATH, "w") as f:
            f.write(response["SecretString"])
    return CA_CERT_PATH


def b64d(s):
    s += '=' * (4 - len(s) % 4)
    return base64.urlsafe_b64decode(s)


def decrypt_pbes2_jwe(token, password):
    """
    Manual decryption algorithm for pbes2. All the other libraries fail or have some sort of problem doing this algo,
    so this does it manually. I'd much rather use a library, but we can't have nice things
    :param token: Input encrypted string
    :param password: Password for string
    :return: Decrypted copy of the input string
    """
    parts = token.split('.')

    if len(parts) != 5:
        raise ValueError("Invalid compact JWE format")

    protected_header_b64 = parts[0]

    header = json.loads(b64d(parts[0]))
    encrypted_key = b64d(parts[1])
    iv = b64d(parts[2])
    ciphertext = b64d(parts[3])
    tag = b64d(parts[4])

    alg = header["alg"]
    enc = header["enc"]
    p2s = b64d(header["p2s"])
    p2c = header["p2c"]

    salt = alg.encode("utf-8") + b"\x00" + p2s

    if alg == "PBES2-HS256+A128KW":
        hash_alg = hashes.SHA256()
        kek_len = 16

    elif alg == "PBES2-HS384+A192KW":
        hash_alg = hashes.SHA384()
        kek_len = 24

    elif alg == "PBES2-HS512+A256KW":
        hash_alg = hashes.SHA512()
        kek_len = 32

    else:
        raise ValueError(f"Unsupported alg: {alg}")

    kdf = PBKDF2HMAC(
        algorithm=hash_alg,
        length=kek_len,
        salt=salt,
        iterations=p2c,
    )
    kek = kdf.derive(
        password.encode() if isinstance(password, str) else password
    )
    cek = aes_key_unwrap(kek, encrypted_key)

    if enc == "A256GCM":

        if len(cek) != 32:
            raise ValueError(
                f"A256GCM requires 32-byte CEK, got {len(cek)}"
            )

        aad = protected_header_b64.encode("ascii")

        aesgcm = AESGCM(cek)

        plaintext_output = aesgcm.decrypt(
            iv,
            ciphertext + tag,
            aad
        )

        return json.loads(plaintext_output)

    raise ValueError(f"Unsupported enc algorithm: {enc}")


def gen_one_time_token(device_csr, device_name):
    """
    One time token generator for the certificate signing request api call. Step-ca requires a one time token to verify
    the identity of the sender(this lambda). Has some specific fields that need to be filled out, which includes piece from
    a decrypted copy of the device provisioner encrypted key(manually decrypted), sha256 fingerprint of the csr, and a
    couple other generic name/current time/expiration fields.
    :param device_csr: Certificate signing request
    :param device_name: Name of the device the csr is for
    :return: One time token string for the request. Valid for 300 seconds after creation.
    """
    # grab step ca pieces from secrets manager, retrieve values needed from config
    provisioner_password = secrets_client.get_secret_value(SecretId="cert-auth/ca-password")["SecretString"].strip()
    ca_config_file = secrets_client.get_secret_value(SecretId="cert-auth/ca-config")["SecretString"]
    ca_config_json = json.loads(ca_config_file)
    provisioner_list = ca_config_json["authority"]["provisioners"]
    provisioner = next(p for p in provisioner_list if p["name"] == "device-provisioner")
    encrypted_key = provisioner["encryptedKey"]

    # decrypt step-ca's json web key from json web encryption
    private_jwk_dict = decrypt_pbes2_jwe(encrypted_key, provisioner_password)
    private_jwk = jwk.JWK(**private_jwk_dict)

    # generate sha256 fingerprint for csr
    loaded_csr = load_pem_x509_csr(device_csr.encode(), default_backend())
    der = loaded_csr.public_bytes(Encoding.DER)
    digest = hashlib.sha256(der).digest()
    csr_fingerprint = base64.urlsafe_b64encode(digest).rstrip(b"=").decode()

    # generate required fields for json web token
    time_now = int(time.time())
    claims = {
        "iss": "device-provisioner",
        "sub": device_name,
        "aud": f"{CA_URL}/1.0/sign",
        "iat": time_now,
        "nbf": time_now,
        "exp": time_now + 300,
        "jti": str(uuid.uuid4()),
        "sans": [],
        "sha": csr_fingerprint
    }
    jwt_token = jwt.JWT(
        header={
            "alg": "ES256",
            "kid": private_jwk.get("kid")
        },
        claims=claims
    )
    jwt_token.make_signed_token(private_jwk)
    return jwt_token.serialize()


def check_ca_health():
    """
    Quick check for certificate authority status, ensuring its running properly. Queries the health api for it,
    verifies the certificate against the certificate authority root certificate, and returns the response
    :return: health response
    """
    ca_cert = get_root_ca_cert()
    response = requests.get(f"{CA_URL}/health", verify=ca_cert)
    return response.json()


def renew_certificate(event, context):
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