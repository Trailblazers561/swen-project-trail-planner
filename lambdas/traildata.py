import json
import boto3
from decimal import Decimal

dynamodb = boto3.resource('dynamodb')

def convert_decimals(obj):
    if isinstance(obj, list):
        return [convert_decimals(i) for i in obj]
    elif isinstance(obj, dict):
        return {k: convert_decimals(v) for k, v in obj.items()}
    elif isinstance(obj, Decimal):
        return float(obj) if obj % 1 > 0 else int(obj)
    else:
        return obj

def get_trail_data(event, context):
    table = dynamodb.Table('traildata_table')

    try:
        response = table.scan()
        traildata = convert_decimals(response.get('Items', []))

        return {
            'statusCode': 200,
            'headers': {
                "Access-Control-Allow-Origin": "*",  
                "Access-Control-Allow-Methods": "GET, POST, OPTIONS",
                "Access-Control-Allow-Headers": "Content-Type, Authorization",
            },
            'body': json.dumps(traildata)
        }
    except Exception as e:
        return {
            'statusCode': 500,
            'body': json.dumps({'error': str(e)})
        }


def upload_trail_data(event, context):
    table = dynamodb.Table('traildata_table')

    if isinstance(event['body'], str):
        body = json.loads(event['body'])
    else:
        body = event['body']

    trail_id = body.get('id')
    trail_name = body.get('name')

    try:
        response = table.put_item(
            Item={
                'id': trail_id,
                'name': trail_name
            }
        )
        return {
            'statusCode': 200,
            'headers': {
                'Access-Control-Allow-Credentials': True,
                'Access-Control-Allow-Origin': '*',
                'Access-Control-Allow-Headers': 'Content-Type,Authorization',
                'Access-Control-Allow-Methods': 'OPTIONS,POST,GET'
            },
            'body': json.dumps({'message': 'Trail data added successfully', 'data': convert_decimals(response)})
        }

    except Exception as e:
        return {
            'statusCode': 500,
            'body': json.dumps({'error': str(e)})
        }