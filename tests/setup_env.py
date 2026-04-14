import boto3
import argparse
from pathlib import Path

cloudfront = boto3.client('cloudfront')
api_gateway = boto3.client('apigateway')
cognito = boto3.client('cognito-idp')

def retrieve_cloudfront_url(DEPLOY_ENV):
    distributions = cloudfront.list_distributions()
    for distribution in distributions["DistributionList"]["Items"]:
        if distribution["Comment"] == f"{DEPLOY_ENV} distribution":
            return distribution["DomainName"]

def retrieve_api_url(env):
    gateways = api_gateway.get_rest_apis(limit=20)
    api_id = ""
    for gateway in gateways["items"]:
        if gateway["name"] == f"{env}_trailplanner_api":
            api_id = gateway["id"]
            return f"https://{api_id}.execute-api.us-east-1.amazonaws.com/{env}_trailplanner_api_stage"

def retrieve_user_pool_id(env):
    pools = cognito.list_user_pools(MaxResults=20)
    for pool in pools["UserPools"]:
        if pool["Name"] == f"{env}_trailplanner_user_pool":
            return pool["Id"]

def retrieve_client_id(env):
    clients = cognito.list_user_pool_clients(UserPoolId=retrieve_user_pool_id(env), MaxResults=20)
    for client in clients["UserPoolClients"]:
        if client["ClientName"] == f"{env}_trailplanner_cognito_client":
            return client["ClientId"]

def retrieve_token(env):
    response = cognito.initiate_auth(
        ClientId=retrieve_client_id(env),
        AuthFlow="USER_PASSWORD_AUTH",
        AuthParameters={
            "USERNAME": "admin@gmail.com",
            "PASSWORD": "testPassword123!"
        }
    )
    return response['AuthenticationResult']['AccessToken']

def write_values(env):
    with open(Path(__file__).parent / ".env", "w") as file:
        # file.write(f"CLOUDFRONT_URL=http://{retrieve_cloudfront_url(env)}\n")
        file.write("CLOUDFRONT_URL=http://d2joobtdyw3u13.cloudfront.net\n")
        file.write(f"API_URL={retrieve_api_url(env)}\n")
        file.write(f"API_TOKEN={retrieve_token(env)}\n")
        file.write(f"API_KEY={env}-trail-planner-key-trail-trail-trail-trail\n")
        file.write(f"LOCAL_RUN={'true' if env == 'local' else 'false'}")

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--env", required=True)
    args = parser.parse_args()
    write_values(args.env)