import os
import json
import boto3
import concurrent.futures
from boto3.dynamodb.conditions import Key, Attr
from decimal import Decimal

dynamodb = boto3.resource('dynamodb')

TRAIL_LOGS_TABLE = os.environ.get("TRAIL_LOGS_TABLE", "trail_device_logs")
TRAIL_METADATA_TABLE = os.environ.get("TRAIL_METADATA_TABLE", "trail_metadata")

logs_table = dynamodb.Table(TRAIL_LOGS_TABLE)
metadata_table = dynamodb.Table(TRAIL_METADATA_TABLE)

def convert_decimals(obj):
    if isinstance(obj, list):
        return [convert_decimals(i) for i in obj]
    elif isinstance(obj, dict):
        return {k: convert_decimals(v) for k, v in obj.items()}
    elif isinstance(obj, Decimal):
        return float(obj) if obj % 1 > 0 else int(obj)
    else:
        return obj

# Helper to query logs for a single trail
def query_trail(trail_id, start=None, end=None):
    if start and end:
        response = logs_table.query(
            KeyConditionExpression=(Key('trail_id').eq(trail_id) & Key('timestamp').between(int(start), int(end)))
        )
    else:
        response = logs_table.query(
            KeyConditionExpression=Key('trail_id').eq(trail_id)
        )
    return response.get('Items', [])

def get_trail_name(trail_id):
    response = metadata_table.get_item(Key={'trail_id': trail_id})
    return response.get('Item', {}).get('trail_name')

def get_trail_data(event, context):
    try:
        query_params = event.get('queryStringParameters', {})
        
        trail_id = query_params.get('trail') if query_params else None
        trails = query_params.get('trails') if query_params else None
        start = query_params.get('start') if query_params else None
        end = query_params.get('end') if query_params else None

        results = []

        if trails:
            trail_ids = [int(tid.strip()) for tid in trails.split(',')]
            with concurrent.futures.ThreadPoolExecutor(max_workers=10) as executor:
                future_to_trail = {
                    executor.submit(query_trail, tid, start, end): tid 
                    for tid in trail_ids
                }
                for future in concurrent.futures.as_completed(future_to_trail):
                    trail_results = future.result()
                    results.extend(trail_results)
        elif trail_id:
            results = query_trail(int(trail_id), start, end)
        elif start and end:
            response = logs_table.scan(
                FilterExpression=Attr("timestamp").between(int(start), int(end))
            )
            results = response.get('Items', [])
        else:
            response = logs_table.scan()
            results = response.get('Items', [])

        # Optionally enrich with trail_name
        for item in results:
            item["trail_name"] = get_trail_name(item["trail_id"])

        return {
            'statusCode': 200,
            'headers': {
                "Access-Control-Allow-Origin": "*",  
                "Access-Control-Allow-Methods": "GET, POST, OPTIONS",
                "Access-Control-Allow-Headers": "Content-Type, Authorization",
            },
            'body': json.dumps(convert_decimals(results))
        }
    except Exception as e:
        return {
            'statusCode': 500,
            'body': json.dumps({'error': str(e)})
        }

def upload_trail_data(event, context):
    if isinstance(event['body'], str):
        body = json.loads(event['body'])
    else:
        body = event['body']

    trail_id = int(body.get('trail_id'))
    data = body.get('data', [])

    try:
        with logs_table.batch_writer() as batch:
            for point in data:
                item = {
                    'trail_id': trail_id,
                    'timestamp': int(point['timestamp'])
                }
                for key, value in point.items():
                    if key != 'timestamp':
                        item[key] = value
                batch.put_item(Item=item)

        return {
            'statusCode': 200,
            'headers': {
                'Access-Control-Allow-Credentials': True,
                'Access-Control-Allow-Origin': '*',
                'Access-Control-Allow-Headers': 'Content-Type,Authorization',
                'Access-Control-Allow-Methods': 'OPTIONS,POST,GET'
            },
            'body': json.dumps({'message': 'Trail data added successfully', 'data': convert_decimals(data)})
        }

    except Exception as e:
        debug = False
        return {
            'statusCode': 500,
            'body': json.dumps({'error': str(e) if debug else "Fatal error"})
        }