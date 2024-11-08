import json
import boto3

dynamodb = boto3.resource('dynamodb')

def get_trail_data(event, context):
    table = dynamodb.Table('traildata_table')

    try:
        response = table.scan()
        products = response.get('Items', [])

        return {
            'statusCode': 200,
            'headers': {
                "Access-Control-Allow-Origin": "*",  
                "Access-Control-Allow-Methods": "GET, POST, OPTIONS",
                "Access-Control-Allow-Headers": "Content-Type, Authorization",
            },
            'body': json.dumps(products)
        }
    except Exception as e:
        return {
            'statusCode': 500,
            'body': json.dumps({'error': str(e)})
        }


def upload_trail_data(event, context):
    table = dynamodb.Table('traildata_table')

    trail_id = event['id']
    trail_name = event['name']

    response = table.put_item(
        Item={
            'id': {'N': trail_id},
            'name': {'S': trail_name}
        }
    )

    return response