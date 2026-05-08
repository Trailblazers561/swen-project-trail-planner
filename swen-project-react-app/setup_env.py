import argparse
import os
from pathlib import Path

import boto3
from botocore.exceptions import ProfileNotFound

try:
    omit_dev_role = os.getenv("OMIT_DEV_ROLE", "false") == "true"
    if omit_dev_role:
        session = boto3
    else:
        session = boto3.Session(profile_name="dev-role")
except ProfileNotFound: 
    session = boto3
    print("dev-role NOT FOUND: THIS IS AN ISSUE FOR A LOCAL RUN")

api_gateway = session.client('apigateway')
cognito = session.client('cognito-idp')

def retrieve_api_url(env):
    gateways = api_gateway.get_rest_apis(limit=20)
    api_id = ""
    for gateway in gateways["items"]:
        if gateway["name"] == f"{env}_trailplanner_public_api":
            api_id = gateway["id"]
            return f"https://{api_id}.execute-api.us-east-1.amazonaws.com/{env}_trailplanner_public_api_stage"

def retrieve_user_pool_id(env):
    pools = cognito.list_user_pools(MaxResults=20)
    for pool in pools["UserPools"]:
        if pool["Name"] == f"{env}_trailplanner_user_pool":
            return pool["Id"]

def retrieve_user_id(env):
    clients = cognito.list_user_pool_clients(UserPoolId=retrieve_user_pool_id(env), MaxResults=20)
    for client in clients["UserPoolClients"]:
        if client["ClientName"] == f"{env}_trailplanner_cognito_client":
            return client["ClientId"]

def write_values(env):
    with open(Path(__file__).parent / ".env", "w") as file:
        file.write(f"VITE_API_URL={retrieve_api_url(env)}\n")
        file.write(f"VITE_COGNITO_REGION=us-east-1\n")
        file.write(f"VITE_COGNITO_USER_POOL_ID={retrieve_user_pool_id(env)}\n")
        file.write(f"VITE_COGNITO_CLIENT_ID={retrieve_user_id(env)}\n")

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--env", required=True)
    args = parser.parse_args()
    write_values(args.env)