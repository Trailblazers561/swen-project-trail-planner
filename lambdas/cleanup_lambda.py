import re

import boto3
from datetime import datetime, timezone, timedelta
import os

s3 = boto3.client('s3')

BUCKET_NAME = os.environ['BUCKET_NAME']


def cleanup(event, context):
    now = datetime.now(timezone.utc)
    cutoff = now - timedelta(hours=48)
    longTermCutoff = now - timedelta(days=30)

    response = s3.list_objects_v2(Bucket=BUCKET_NAME)

    if 'Contents' not in response:
        return {'message': 'No files to delete.'}

    to_delete = []
    for obj in response['Contents']:
        key = obj['Key']
        if re.match(r'^import-hashes/[0-9a-f]{64}\.json$', key):  # special exception for our hash import files
            if obj['LastModified'] < longTermCutoff:
                to_delete.append({'Key': key})
        else:
            if obj['LastModified'] < cutoff:
                to_delete.append({'Key': key})

    if to_delete:
        s3.delete_objects(Bucket=BUCKET_NAME, Delete={'Objects': to_delete})
        return {'message': f'Deleted {len(to_delete)} files.'}
    else:
        return {'message': 'No files older than their expiration dates'}
