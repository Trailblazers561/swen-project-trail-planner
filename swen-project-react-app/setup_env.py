import boto3

session = boto3.Session(profile_name="dev-role")

api_gateway = session.client('apigateway')
cognito = session.client('cognito-idp')

def retrieve_values(env):

    api_url = retrieve_api_url(env)
    region = "us-east-1"
    user_pool_id = retrieve_user_pool_id(env)
    client_id = retrieve_user_id(env, user_pool_id)

    return {
        "VITE_API_URL": api_url,
        "VITE_COGNITO_REGION": region,
        "VITE_COGNITO_USER_POOL_ID": user_pool_id, 
        "VITE_COGNITO_CLIENT_ID": client_id
    }

def retrieve_api_url(env):
    gateways = api_gateway.get_rest_apis(limit=20)
    api_id = ""
    for gateway in gateways["items"]:
        if gateway["name"] == f"{env}trailplanner_api":
            api_id = gateway["id"]
            return f"https://{api_id}.execute-api.us-east-1.amazonaws.com/{env}trailplanner_api_stage"

def retrieve_user_pool_id(env):
    pools = cognito.list_user_pools(MaxResults=20)
    for pool in pools["UserPools"]:
        if pool["Name"] == f"{env}trailplanner_user_pool":
            return pool["Id"]

def retrieve_user_id(env, user_pool_id):
    clients = cognito.list_user_pool_clients(UserPoolId=user_pool_id, MaxResults=20)
    for client in clients["UserPoolClients"]:
        if client["ClientName"] == f"{env}trailplanner_cognito_client":
            return client["ClientId"]

def write_values(env):
    values = retrieve_values(env)
    with open(".env", "w") as file:
        file.write(f"VITE_API_URL={values['VITE_API_URL']}\n")
        file.write(f"VITE_COGNITO_REGION={values['VITE_COGNITO_REGION']}\n")
        file.write(f"VITE_COGNITO_USER_POOL_ID={values['VITE_COGNITO_USER_POOL_ID']}\n")
        file.write(f"VITE_COGNITO_CLIENT_ID={values['VITE_COGNITO_CLIENT_ID']}\n")

write_values("tst_")