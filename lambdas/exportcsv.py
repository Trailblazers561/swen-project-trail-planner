import os
import json
import time
import boto3
from boto3.dynamodb.conditions import Key, Attr
from decimal import Decimal
from pprint import pprint

dynamodb = boto3.resource('dynamodb')

# Table references
logs_table = dynamodb.Table(os.environ.get("TRAIL_LOGS_TABLE", "local_TrailDeviceLogs"))
trail_metadata_table = dynamodb.Table(os.environ.get("TRAIL_METADATA_TABLE", "local_TrailMetadata"))
device_metadata_table = dynamodb.Table(os.environ.get("DEVICE_METADATA_TABLE", "local_DeviceMetadata"))
trail_groups_table = dynamodb.Table(os.environ.get("TRAIL_GROUPS_TABLE", "local_TrailGroups"))

def convert_decimals(obj):
    if isinstance(obj, list):
        return [convert_decimals(i) for i in obj]
    elif isinstance(obj, dict):
        return {k: convert_decimals(v) for k, v in obj.items()}
    elif isinstance(obj, Decimal):
        return float(obj) if obj % 1 > 0 else int(obj)
    else:
        return obj


def get_all_db_data(event, context):
    items = logs_table.scan()

    return pprint(json.dumps(convert_decimals(items)))

def get_specific_db_data(event, context):

    items=device_metadata_table.scan(
        FilterExpression=Attr("device_id").eq("deviceB")
    )

    return pprint(json.dumps(convert_decimals(items)))


if __name__ == "__main__":
    print(get_specific_db_data(None, None))