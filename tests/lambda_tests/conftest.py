import os

import boto3
import pytest
from moto import mock_aws


AWS_REGION = "us-east-1"


def create_table(dynamodb, table_name, partition_key):
    """
    Creates a DynamoDB table with a simple HASH partition key.
    """
    table = dynamodb.create_table(
        TableName=table_name,
        KeySchema=[
            {
                "AttributeName": partition_key,
                "KeyType": "HASH",
            }
        ],
        AttributeDefinitions=[
            {
                "AttributeName": partition_key,
                "AttributeType": "S",
            }
        ],
        BillingMode="PAY_PER_REQUEST",
    )

    table.wait_until_exists()
    return table


@pytest.fixture(scope="function")
def aws():
    """
    Spins up a fresh mocked AWS environment for every test.
    """

    os.environ["AWS_DEFAULT_REGION"] = AWS_REGION
    os.environ["AREA_TABLE"] = "test_trailcount_area_table"
    os.environ["TRAIL_TABLE"] = "test_trailcount_trail_table"
    os.environ["DEVICE_TABLE"] = "test_trailcount_device_table"
    from sample_data.load_test_data import load_test_data

    with mock_aws():
        dynamodb = boto3.resource(
            "dynamodb",
            region_name=AWS_REGION,
        )

        tables = {
            "area": create_table(
                dynamodb,
                os.environ["AREA_TABLE"],
                "name",
            ),
            "trail": create_table(
                dynamodb,
                os.environ["TRAIL_TABLE"],
                "id",
            ),
            "device": create_table(
                dynamodb,
                os.environ["DEVICE_TABLE"],
                "id",
            ),
        }
        load_test_data("test")

        yield tables