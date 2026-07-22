import base64
import hashlib
import json
import os
import time
import uuid
from datetime import datetime, timedelta
from decimal import Decimal
from zoneinfo import ZoneInfo

import boto3
from boto3.dynamodb.conditions import Attr, Key
import requests
from jwcrypto import jwk, jwt
from cryptography.hazmat.backends import default_backend
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.ciphers.aead import AESGCM
from cryptography.hazmat.primitives.keywrap import aes_key_unwrap
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC
from cryptography.hazmat.primitives.serialization import Encoding
from cryptography.x509 import load_pem_x509_csr

dynamodb = boto3.resource('dynamodb')
secrets_client = boto3.client("secretsmanager")

device_trail_log_hour_table = dynamodb.Table(
    os.environ.get("DEVICE_TRAIL_LOG_HOUR_TABLE", "local_trailcount_device_trail_log_hour_table"))
device_trail_log_day_table = dynamodb.Table(
    os.environ.get("DEVICE_TRAIL_LOG_DAY_TABLE", "local_trailcount_device_trail_log_day_table"))
device_trail_log_week_table = dynamodb.Table(
    os.environ.get("DEVICE_TRAIL_LOG_WEEK_TABLE", "local_trailcount_device_trail_log_week_table"))
device_trail_log_month_table = dynamodb.Table(
    os.environ.get("DEVICE_TRAIL_LOG_MONTH_TABLE", "local_trailcount_device_trail_log_month_table"))
trail_table = dynamodb.Table(os.environ.get("TRAIL_TABLE", "local_trailcount_trail_table"))
device_table = dynamodb.Table(os.environ.get("DEVICE_TABLE", "local_trailcount_device_table"))
device_trail_table = dynamodb.Table(os.environ.get("DEVICE_TRAIL_TABLE", "local_trailcount_device_trail_table"))
area_table = dynamodb.Table(os.environ.get("AREA_TABLE", "local_trailcount_area_table"))
device_log_table = dynamodb.Table(os.environ.get("DEVICE_LOG_TABLE", "local_trailcount_device_log_table"))
registration_table = dynamodb.Table(os.environ.get("REGISTRATION_TABLE", "local_trailcount_registration_table"))

table_time_map = {
    "hour": device_trail_log_hour_table,
    "day": device_trail_log_day_table,
    "week": device_trail_log_week_table,
    "month": device_trail_log_month_table,
    "year": device_trail_log_month_table
}

CA_URL = os.environ.get("CERTIFICATE_AUTHORITY_URL")
s3_client = boto3.client('s3')
csv_bucket = os.environ.get("TRAIL_CSV_BUCKET")
v1_device_bucket = os.environ.get("V1_DEVICE_BUCKET")

cognito = boto3.client('cognito-idp')
COGNITO_USER_POOL_ID = os.environ.get("COGNITO_USER_POOL_ID")
user_groups = {"user": 0, "trail_manager": 1, "admin": 2, "root_admin": 3}
CA_CERT_PATH = "/tmp/root_ca.crt"


def device_secret_id(device_name):
    """
    Quick conversion helper that converts from device name to the actual secrets manager path that's appended with the
    deploy env. Ex "deviceName" in "prod" becomes "prod/deviceName"
    :param device_name: Device name
    :return: Environment appended to the device name as the path
    """
    return f"{os.environ['DEPLOY_ENV']}/{device_name}"


def ca_secret_id(name):
    """
    Quick conversion helper that converts from cert-auth filename to the actual secrets manager path that's appended with the
    deploy env. Ex "root-cert" in "prod" becomes "prod/cert-auth/root-cert"
    :param name: File name
    :return: Environment appended to the file name as the path
    """
    return f"{os.environ['DEPLOY_ENV']}/cert-auth/{name}"


def check_ca_health():
    """
    Quick check for certificate authority status, ensuring its running properly. Queries the health api for it,
    verifies the certificate against the certificate authority root certificate, and returns the response
    :return: health response
    """
    if not CA_URL:
        return {"status": "error",
                "message:": "Certificate Authority URL not configured, or broken environment variable"}
    ca_cert = get_root_ca_cert()
    response = requests.get(f"{CA_URL}/health", verify=ca_cert)
    return response.json()


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
    provisioner_password = secrets_client.get_secret_value(SecretId=ca_secret_id("ca-password"))["SecretString"].strip()
    ca_config_file = secrets_client.get_secret_value(SecretId=ca_secret_id("ca-config"))["SecretString"]
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


def get_root_ca_cert():
    """
    Get the root ca certificate from secrets manager, and saves it locally at
    tmp/root_ca.crt
    :return: path to the root ca file
    """
    if not os.path.exists(CA_CERT_PATH):
        os.makedirs("/tmp", exist_ok=True)  # should already exist but redundancy is great
        sm = boto3.client("secretsmanager")
        response = sm.get_secret_value(SecretId=ca_secret_id("root-ca-cert"))
        with open(CA_CERT_PATH, "w") as f:
            f.write(response["SecretString"])
    return CA_CERT_PATH


def convert_decimals(obj):
    if isinstance(obj, list):
        return [convert_decimals(i) for i in obj]
    elif isinstance(obj, dict):
        return {k: convert_decimals(v) for k, v in obj.items()}
    elif isinstance(obj, Decimal):
        return float(obj) if float(obj) % 1 > 0 else int(obj)
    else:
        return obj


def timestamp_conversion(timestamp, time_increment):
    """
    Convert timestamp back to start of day/week/month as need be for higher grade time tables
    :param timestamp: unix timestamp of current time
    :param time_increment: string of day/week/month to convert it to
    :return: timestamp of the start of that period, none if invalid time increment
    """
    dt_timestamp = datetime.fromtimestamp(timestamp, tz=ZoneInfo("America/New_York"))
    if time_increment == "hour":
        return int(dt_timestamp.replace(minute=0, second=0, microsecond=0).timestamp())
    elif time_increment == "day":
        return int(dt_timestamp.replace(hour=0, minute=0, second=0, microsecond=0).timestamp())
    elif time_increment == "week":
        monday = dt_timestamp - timedelta(days=dt_timestamp.weekday())
        return int(monday.replace(hour=0, minute=0, second=0, microsecond=0).timestamp())
    elif time_increment == "month":
        return int(dt_timestamp.replace(day=1, hour=0, minute=0, second=0, microsecond=0).timestamp())
    return None


def get_next_registration_id() -> int:
    print("Retrieving next registration_id")
    # Get all existing registrations to find next available ID
    try:
        resp = registration_table.scan()
        existing_registrations = resp.get("Items", [])
        if existing_registrations:
            existing_ids = [int(r.get("registration_id", 0)) for r in existing_registrations]
            new_registration_id = max(existing_ids, default=0) + 1
        else:
            new_registration_id = 1
    except Exception as e:
        print(f"Error finding max registration_id, starting with 1. Exception: {e}")
        # If scan fails, start with ID 1
        new_registration_id = 1

    return new_registration_id


def get_next_trail_id() -> int:
    print("Retrieving next trail_id")
    # Get all existing trails to find next available ID
    try:
        resp = trail_table.scan()
        existing_trails = resp.get("Items", [])
        if existing_trails:
            existing_ids = [int(t.get("id", 0)) for t in existing_trails]
            new_trail_id = max(existing_ids, default=0) + 1
        else:
            new_trail_id = 1
    except Exception as e:
        print(f"Error finding max trail_id, starting with 1. Exception: {e}")
        # If scan fails, start with ID 1
        new_trail_id = 1

    return new_trail_id


def get_next_device_id() -> int:
    print("Retrieving next device_id")
    # Get all existing devices to find next available ID
    try:
        resp = device_table.scan()
        existing_devices = resp.get("Items", [])
        if existing_devices:
            existing_ids = [int(d.get("id", 0)) for d in existing_devices]
            new_device_id = max(existing_ids, default=0) + 1
        else:
            new_device_id = 1
    except Exception as e:
        print(f"Error finding max device_id, starting with 1. Exception: {e}")
        # If scan fails, start with ID 1
        new_device_id = 1

    return new_device_id


def get_next_device_trail_id() -> int:
    print("Retrieving next device_trail_id")
    # Get all existing device_trails to find next available ID
    try:
        resp = device_trail_table.scan()
        existing_device_trails = resp.get("Items", [])
        if existing_device_trails:
            existing_ids = [int(dt.get("id", 0)) for dt in existing_device_trails]
            new_device_trail_id = max(existing_ids, default=0) + 1
        else:
            new_device_trail_id = 1
    except Exception as e:
        print(f"Error finding max device_trail_id, starting with 1. Exception: {e}")
        # If scan fails, start with ID 1
        new_device_trail_id = 1

    return new_device_trail_id


def get_device_trail_id(device_id, trail_id=None):
    """
    given the device id get the devicetrail id that we need for the time entries
    :param device_id: device id
    :param trail_id: trail id, optional but useful to prevent issues.
    :return: devicetrail id
    """
    if trail_id is None:
        items = device_trail_table.query(
            KeyConditionExpression=Key("device_id").eq(device_id),
            ScanIndexForward=False,
            Limit=1
        ).get("Items", [])
    else:
        items = device_trail_table.query(
            KeyConditionExpression=Key("device_id").eq(device_id),
            FilterExpression=Attr("trail_id").eq(trail_id),
            ScanIndexForward=False,
            Limit=1
        ).get("Items", [])
    if not items:
        raise ValueError(f"No device trail association with device id {device_id}, trail_id={trail_id} found")
    return int(items[0]["id"]), int(items[0]["trail_id"])  # just return the ids, dont need all that


def is_device_blocked(device_id=None, device_name=None) -> bool:
    """
    Slapped together check for the is blocked value in device. If a device is blocked, we're ignoring any data from it.
    """
    if device_id is not None:
        response = device_table.get_item(Key={"id": int(device_id)})
        item = response.get("Item")
    elif device_name is not None:
        items = device_table.query(
            IndexName="name-index",
            KeyConditionExpression=Key("name").eq(device_name),
            Limit=1
        ).get("Items", [])
        item = items[0] if items else None
    else:
        raise ValueError("Must provide either device_id or device_name")

    if not item:
        raise ValueError(f"Device not found")

    return bool(item.get("is_blocked", False))


def is_device_archived(device_id=None, device_name=None) -> bool:
    """
    Slapped together check for the is blocked value in device. If a device is archived, we're ignoring any data from it.
    Maybe some more features, dont know
    """
    if device_id is not None:
        response = device_table.get_item(Key={"id": int(device_id)})
        item = response.get("Item")
    elif device_name is not None:
        items = device_table.query(
            IndexName="name-index",
            KeyConditionExpression=Key("name").eq(device_name),
            Limit=1
        ).get("Items", [])
        item = items[0] if items else None
    else:
        raise ValueError("Must provide either device_id or device_name")

    if not item:
        raise ValueError(f"Device not found")

    return bool(item.get("is_archived", False))


def cors_headers():
    return {
        "Access-Control-Allow-Origin": "*",
        "Access-Control-Allow-Methods": "GET,POST,PUT,DELETE,OPTIONS",
        "Access-Control-Allow-Headers": "Content-Type,Authorization"
    }
