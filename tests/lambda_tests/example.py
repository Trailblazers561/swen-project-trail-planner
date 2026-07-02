from lambda_config import update_sys_path
update_sys_path()

import boto3
from moto import mock_aws
from lambdas.public_api.trail_metadata.trail_metadata_get import get_trail_metadata

@mock_aws
def test_get_all_trails(monkeypatch):
    dynamodb = boto3.resource("dynamodb", region_name="us-east-1")

    table = dynamodb.create_table(
        TableName="trail",
        KeySchema=[
            {"AttributeName": "id", "KeyType": "HASH"}
        ],
        AttributeDefinitions=[
            {"AttributeName": "id", "AttributeType": "N"}
        ],
        BillingMode="PAY_PER_REQUEST",
    )

    table.put_item(Item={
        "id": 1,
        "name": "Trail A"
    })

    import lambdas.public_api.trail_metadata.trail_metadata_get as handler

    monkeypatch.setattr(handler, "trail_table", table)
    monkeypatch.setattr(handler, "dynamodb", boto3.client("dynamodb"))

    event = {
        "queryStringParameters": {},
        "multiValueQueryStringParameters": {}
    }

    response = get_trail_metadata(event, None)

    assert response["statusCode"] == 200
    assert len(response["body"])
    print(response)