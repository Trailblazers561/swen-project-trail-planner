import os
import json
import uuid
import boto3

s3_client = boto3.client('s3')

# Table references
s3_bucket = os.environ.get("TRAIL_S3_BUCKET")


def generate_url(event, context):
    """
    When we want to upload a csv file, we'll store it in our bucket, so create a url that the frontend can send the
    file to in order to store it in our s3 bucket for parsing to the db.
    """
    try:
        fullFilePath = "tmp-upload/" + str(uuid.uuid4()) + "/trail_data.csv"

        url = s3_client.generate_presigned_url('put_object',
                                               Params={'Bucket': s3_bucket,
                                                       'Key': fullFilePath},
                                               ExpiresIn=3600)
        print(f"file path {fullFilePath} generated to upload file to")
        return {
            "statusCode": 200,
            "headers": cors_headers(),
            "body": json.dumps({"uploadUrl": url, "s3FilePath": fullFilePath})
        }
    except Exception as e:
        return {
            "statusCode": 500,
            "headers": cors_headers(),
            "body": json.dumps({"error": f"Internal server error: {str(e)}"})
        }


def cors_headers():
    return {
        "Access-Control-Allow-Origin": "*",
        "Access-Control-Allow-Methods": "GET,OPTIONS",
        "Access-Control-Allow-Headers": "Content-Type,Authorization"
    }
