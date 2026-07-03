import os
import sys
import boto3
import pytest
from moto import mock_aws
import importlib
from lambda_config import update_sys_path

#
# --------------------------------------------------------------------------
# Python Path
# --------------------------------------------------------------------------
#
update_sys_path()

#
# --------------------------------------------------------------------------
# Environment Variables
# --------------------------------------------------------------------------
#

AWS_REGION = "us-east-1"
ENV = "test"
TABLES = {
    "AREA_TABLE": f"{ENV}_trailcount_area_table",
    "TRAIL_TABLE": f"{ENV}_trailcount_trail_table",
    "DEVICE_TABLE": f"{ENV}_trailcount_device_table",
    "DEVICE_TRAIL_TABLE": f"{ENV}_trailcount_device_trail_table",
    "DEVICE_LOG_TABLE": f"{ENV}_trailcount_device_log_table",
    "REGISTRATION_TABLE": f"{ENV}_trailcount_registration_table",
    "DEVICE_TRAIL_LOG_HOUR_TABLE": f"{ENV}_trailcount_device_trail_log_hour_table",
    "DEVICE_TRAIL_LOG_DAY_TABLE": f"{ENV}_trailcount_device_trail_log_day_table",
    "DEVICE_TRAIL_LOG_WEEK_TABLE": f"{ENV}_trailcount_device_trail_log_week_table",
    "DEVICE_TRAIL_LOG_MONTH_TABLE": f"{ENV}_trailcount_device_trail_log_month_table",
}

def load_test_data_module():
    """
    Import (or reload) the Lambda after Moto has created the mocked AWS resources.
    This ensures the module's global DynamoDB objects point at Moto instead of real AWS.
    """

    module = importlib.import_module("sample_data.load_test_data")
    return importlib.reload(module)

def set_environment():
    os.environ["AWS_DEFAULT_REGION"] = AWS_REGION
    for key, value in TABLES.items():
        os.environ[key] = value
        os.environ["TRAIL_CSV_BUCKET"] = "local-trailcount-csv"
        os.environ["COGNITO_USER_POOL_ID"] = "local-user-pool"
        os.environ["CERTIFICATE_AUTHORITY_URL"] = "https://localhost"

#
# --------------------------------------------------------------------------
# DynamoDB Helpers
# --------------------------------------------------------------------------
#
def create_table(
    dynamodb,
    table_name,
    partition_key,
    partition_type,
    sort_key=None,
    sort_type=None,
    global_secondary_indexes=None,
):

    key_schema = [
        {"AttributeName": partition_key, "KeyType": "HASH"}
    ]

    attribute_definitions = {
        partition_key: partition_type,
    }

    if sort_key:
        key_schema.append(
            {"AttributeName": sort_key, "KeyType": "RANGE"}
        )
        attribute_definitions[sort_key] = sort_type

    if global_secondary_indexes:
        for gsi in global_secondary_indexes:
            for key in gsi["KeySchema"]:
                attr = key["AttributeName"]

                # skip duplicates
                if attr not in attribute_definitions:
                    # assume S unless you pass type explicitly (see note below)
                    attribute_definitions[attr] = "S"

    kwargs = {
        "TableName": table_name,
        "KeySchema": key_schema,
        "AttributeDefinitions": [
            {"AttributeName": k, "AttributeType": v}
            for k, v in attribute_definitions.items()
        ],
        "BillingMode": "PAY_PER_REQUEST",
    }

    if global_secondary_indexes:
        kwargs["GlobalSecondaryIndexes"] = global_secondary_indexes

    table = dynamodb.create_table(**kwargs)
    table.wait_until_exists()
    return table

def create_tables():
    dynamodb = boto3.resource("dynamodb", region_name=AWS_REGION)
    # Area
    create_table( dynamodb,
        TABLES["AREA_TABLE"],
        "name",
        "S"
    )

    # Trail
    create_table(
        dynamodb,
        TABLES["TRAIL_TABLE"],
        "id",
        "N"
    )

    # Device
    create_table(
        dynamodb,
        TABLES["DEVICE_TABLE"],
        "id",
        "N",
        global_secondary_indexes=[
            {
                "IndexName": "name-index",
                "KeySchema": [
                    {"AttributeName": "name", "KeyType": "HASH"}
                ],
                "Projection": {"ProjectionType": "ALL"},
            }
        ],
    )

    # Device Trail
    create_table(
        dynamodb,
        TABLES["DEVICE_TRAIL_TABLE"],
        "device_id",
        "N",
        sort_key="id",
        sort_type="N",
        global_secondary_indexes=[
            {
                "IndexName": "trail-index",
                "KeySchema": [
                    {
                        "AttributeName": "trail_id",
                        "KeyType": "HASH",
                    }
                ],
                "Projection": {
                    "ProjectionType": "ALL"
                },
            }
        ],
    )

    # Registration
    create_table(
        dynamodb,
        TABLES["REGISTRATION_TABLE"],
        "registration_id",
        "N"
    )

    # Device Log
    create_table(
        dynamodb,
        TABLES["DEVICE_LOG_TABLE"],
        "device_id",
        "N",
        sort_key="time",
        sort_type="N"
    )

    # Hour / Day / Week / Month
    for table in [
        TABLES["DEVICE_TRAIL_LOG_HOUR_TABLE"],
        TABLES["DEVICE_TRAIL_LOG_DAY_TABLE"],
        TABLES["DEVICE_TRAIL_LOG_WEEK_TABLE"],
        TABLES["DEVICE_TRAIL_LOG_MONTH_TABLE"]
    ]:
        create_table(
            dynamodb,
            table,
            "device_trail_id",
            "N",
            sort_key="start",
            sort_type="N"
        )

#
# --------------------------------------------------------------------------
# Fixtures
# --------------------------------------------------------------------------
#
@pytest.fixture(autouse=True)
def aws_environment():
    set_environment()
    with mock_aws():
        create_tables()
        # Populate DynamoDB
        module = load_test_data_module()
        module.load_test_data(ENV)

        # Tests execute here
        yield

@pytest.fixture(autouse=True)
def reload_lambda_modules():
    for module in list(sys.modules):
        if module.startswith("lambdas."):
            del sys.modules[module]