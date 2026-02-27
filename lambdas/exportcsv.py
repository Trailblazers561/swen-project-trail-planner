import os
import json
import time
import boto3
from boto3.dynamodb.conditions import Key, Attr
from decimal import Decimal
from pprint import pprint
import csv
from pathlib import Path
import hashlib



dynamodb = boto3.resource('dynamodb')
s3_client = boto3.client('s3')

# Table references
logs_table = dynamodb.Table(os.environ.get("TRAIL_LOGS_TABLE", "local_TrailDeviceLogs"))
trail_metadata_table = dynamodb.Table(os.environ.get("TRAIL_METADATA_TABLE", "local_TrailMetadata"))
device_metadata_table = dynamodb.Table(os.environ.get("DEVICE_METADATA_TABLE", "local_DeviceMetadata"))
trail_groups_table = dynamodb.Table(os.environ.get("TRAIL_GROUPS_TABLE", "local_TrailGroups"))
s3_bucket = os.environ.get("TRAIL_S3_BUCKET", "local-bucket222222222-13295087")


def convert_decimals(obj):
    if isinstance(obj, list):
        return [convert_decimals(i) for i in obj]
    elif isinstance(obj, dict):
        return {k: convert_decimals(v) for k, v in obj.items()}
    elif isinstance(obj, Decimal):
        return float(obj) if obj % 1 > 0 else int(obj)
    else:
        return obj


def create_and_fill_csv(event, context):
    # So I'm leaving a lot of code *out* because we're swapping to an sql based DB shortly and I'm not going to be putting
    # in extra work. What needs to go here is the queries for whatever csv info we want on the trail data, such as
    # date range, devices, etc etc. Easy enough to just toss some params from context into the sql statement.

    # query goes here "from devices select * where device_id=%s and date = %s" or what have you, figure it out
    items = device_metadata_table.scan(
        FilterExpression=Attr("device_id").eq("deviceB")
    )

    # hopefully the DB output style stays the same as I'm expecting(a list of tuples)
    # this is just some test data in the meantime to simulate it. I'll switch it to the proper column headers once we finalize that.
    items = [("deviceB", 2, 88, 1759065344), ("deviceA", 1, 26, 1234567890)]

    key = "/tmp/trail_data_export.csv"
    file_path = Path(key)
    file_path.parent.mkdir(parents=True, exist_ok=True)

    f = open(key, "w+")
    temp_csv_file = csv.writer(f)

    # non finalized headers. update with sql database structure
    temp_csv_file.writerow(["Device Name", "Trail ID", "Battery %", "Last Update Timestamp"])

    for entry in items:
        temp_csv_file.writerow([entry[0], entry[1], entry[2], entry[3]])

    f.close()

    h = hashlib.sha3_512()
    h.update(json.dumps(items, sort_keys=True).encode('utf-8'))
    fullFilePath = h.hexdigest() + "/trail_data.csv"
    s3_client.upload_file(key, s3_bucket, fullFilePath)

    response = s3_client.generate_presigned_url('get_object',
                                                Params={'Bucket': s3_bucket,
                                                        'Key': fullFilePath},
                                                ExpiresIn=3600)

    return response


if __name__ == "__main__":
    print(create_and_fill_csv(None, None))
