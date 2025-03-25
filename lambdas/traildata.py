import json
import boto3
import concurrent.futures
from boto3.dynamodb.conditions import Key
from boto3.dynamodb.conditions import Attr
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

#Helper function to query a single trail
def query_trail(table, trail_id, start=None, end=None):
    if start and end:
        response = table.query(
            KeyConditionExpression=(Key('id').eq(trail_id) & Key('timestamp').between(int(start), int(end)))
        )
    else:
        response = table.query(
            KeyConditionExpression=Key('id').eq(trail_id)
        )
    return response.get('Items', [])

def get_trail_data(event, context):
    table = dynamodb.Table('traildata_table')

    try:
        query_params = event.get('queryStringParameters', {})
        
        trail_id = query_params.get('trail') if query_params else None
        trails = query_params.get('trails') if query_params else None
        start = query_params.get('start') if query_params else None
        end = query_params.get('end') if query_params else None

        if trails:
            trail_ids = [int(tid.strip()) for tid in trails.split(',')]

            #Use multi threading to speed up lambda execution and improve cost efficiency
            #Should try to only request a max of 10 trails with one query
            with concurrent.futures.ThreadPoolExecutor(max_workers=10) as executor:
                future_to_trail = {
                    executor.submit(query_trail, table, tid, start, end): tid 
                    for tid in trail_ids
                }
                
                results = []
                for future in concurrent.futures.as_completed(future_to_trail):
                    trail_results = future.result()
                    results.extend(trail_results)
            
            traildata = convert_decimals(results)
        elif trail_id:
            response = query_trail(table, int(trail_id), start, end)
            traildata = convert_decimals(response)
        elif start and end:
            response = table.scan(
                FilterExpression=Attr("timestamp").between(int(start), int(end))
            )
            traildata = convert_decimals(response.get('Items', []))
        else:
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
        
        #Change to see exact errors, but in production build we should not give too much info away with error msg
        debug = False
        return {
            'statusCode': 500,
            'body': json.dumps({'error': str(e) if debug else "Fatal error"})
        }


def upload_trail_data(event, context):
    table = dynamodb.Table('traildata_table')

    if isinstance(event['body'], str):
        body = json.loads(event['body'])
    else:
        body = event['body']

    trail_id = body.get('id')
    data = body.get('data', [])

    try:
        #Probably not the most effcient approach use concurrency in future
        with table.batch_writer() as batch:
            for point in data:
                item = {
                    'id': int(trail_id), #partition key
                    'timestamp': int(point.get('timestamp')) #sort key
                }

                #Add possible other columns if they exist in req body
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
        
        #Change to see exact errors, but in production build we should not give too much info away with error msg
        debug = False
        return {
            'statusCode': 500,
            'body': json.dumps({'error': str(e) if debug else "Fatal error"})
        }