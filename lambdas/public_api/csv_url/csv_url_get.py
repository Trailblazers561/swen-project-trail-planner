import json
import uuid

from helper_functions import csv_bucket, s3_client, cors_headers

def generate_url(event, context):
    """
    When we want to upload a csv file, we'll store it in our bucket, so create a url that the frontend can send the
    file to in order to store it in our s3 bucket for parsing to the db.
    """
    try:
        fullFilePath = "tmp-upload/" + str(uuid.uuid4()) + "/trail_data.csv"

        url = s3_client.generate_presigned_url('put_object',
                                               Params={'Bucket': csv_bucket,
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