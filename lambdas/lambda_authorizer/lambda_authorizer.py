import os
import json
import time
import urllib.request
from jose import jwk, jwt
from jose.utils import base64url_decode

COGNITO_USER_POOL_ID = os.environ.get("COGNITO_USER_POOL_ID")
COGNITO_APP_CLIENT_ID = os.environ.get("COGNITO_APP_CLIENT_ID")

ROOT_ADMIN = os.environ.get("ROOT_ADMIN")
ADMIN = os.environ.get("ADMIN")
TRAIL_MANAGER = os.environ.get("TRAIL_MANAGER")
USER = os.environ.get("USER")
GUEST = "GUEST"

group_values = {"guest": 0, "user": 1, "trail_manager": 2, "admin": 3, "root_admin": 4}
groups_simplified = {ROOT_ADMIN: "root_admin", ADMIN: "admin", TRAIL_MANAGER: "trail_manager", USER: "user", GUEST: "guest"}

# Does not handle guest permissions, future sprint task?
PERMISSIONS = {
    ("/csv", "GET"): [ROOT_ADMIN, ADMIN, TRAIL_MANAGER, USER],
    ("/csv", "POST"): [ROOT_ADMIN, ADMIN, TRAIL_MANAGER],
    ("/csv_url", "GET"): [ROOT_ADMIN, ADMIN, TRAIL_MANAGER],
    ("/device_metadata", "GET"): [ROOT_ADMIN, ADMIN, TRAIL_MANAGER, USER, GUEST],
    ("/device_metadata", "PUT"): [ROOT_ADMIN, ADMIN, TRAIL_MANAGER],
    ("/devices", "POST"): [ROOT_ADMIN, ADMIN, TRAIL_MANAGER],
    ("/devices", "PUT"): [ROOT_ADMIN, ADMIN, TRAIL_MANAGER],
    ("/device_management", "GET"): [ROOT_ADMIN, ADMIN, TRAIL_MANAGER],
    ("/block", "PUT"): [ROOT_ADMIN, ADMIN, TRAIL_MANAGER],
    ("/archive", "PUT"): [ROOT_ADMIN, ADMIN, TRAIL_MANAGER],
    ("/heatmap", "GET"): [ROOT_ADMIN, ADMIN, TRAIL_MANAGER, USER, GUEST],
    ("/trail_data", "GET"): [ROOT_ADMIN, ADMIN, TRAIL_MANAGER, USER, GUEST],
    ("/trail_data", "POST"): [ROOT_ADMIN, ADMIN, TRAIL_MANAGER],
    ("/areas", "GET"): [ROOT_ADMIN, ADMIN, TRAIL_MANAGER, USER, GUEST],
    ("/areas", "POST"): [ROOT_ADMIN, ADMIN, TRAIL_MANAGER],
    ("/areas", "PUT"): [ROOT_ADMIN, ADMIN, TRAIL_MANAGER],
    ("/areas", "DELETE"): [ROOT_ADMIN, ADMIN, TRAIL_MANAGER],
    ("/trail_metadata", "GET"): [ROOT_ADMIN, ADMIN, TRAIL_MANAGER, USER, GUEST],
    ("/trail_metadata", "POST"): [ROOT_ADMIN, ADMIN, TRAIL_MANAGER],
    ("/trail_metadata", "PUT"): [ROOT_ADMIN, ADMIN, TRAIL_MANAGER],
    ("/trail_metadata", "DELETE"): [ROOT_ADMIN, ADMIN, TRAIL_MANAGER],
    ("/users", "GET"): [ROOT_ADMIN, ADMIN],
    ("/users", "PUT"): [ROOT_ADMIN, ADMIN],
    ("/users", "DELETE"): [ROOT_ADMIN, ADMIN],
    ("/registration", "GET"): [ROOT_ADMIN, ADMIN, TRAIL_MANAGER],
    ("/registration", "POST"): [ROOT_ADMIN, ADMIN, TRAIL_MANAGER],
    ("/registration", "PUT"): [ROOT_ADMIN, ADMIN, TRAIL_MANAGER],
    ("/registration", "DELETE"): [ROOT_ADMIN, ADMIN, TRAIL_MANAGER],
}

# Download public keys when lambda is created (code is outside handler)
keys = None

def get_keys():
    global keys

    if keys is None:
        keys_url = (f"https://cognito-idp.us-east-1.amazonaws.com/"f"{COGNITO_USER_POOL_ID}/.well-known/jwks.json")

        with urllib.request.urlopen(keys_url) as f:
            response = f.read()

        keys = json.loads(response.decode())["keys"]

    return keys

def handler(event, context):
    print(event)

    policy_resource = event['methodArn']
    resource, http_method = parse_method_arn(policy_resource)

    token_data = parse_token_data(event)

    try:
        # token_data["valid"] means they found a token to validate
        if token_data["valid"]:
            claims = validate_token(token_data["token"])
            if not claims:
                return get_deny_policy("invalid-token", policy_resource)
            users_groups = claims.get("cognito:groups", [GUEST])
        else:
            claims = {}
            users_groups = [GUEST]
        context = {"caller_role": max([groups_simplified[group] for group in users_groups if group in groups_simplified], key=lambda x: group_values[x], default="guest")}

        allowed_groups = PERMISSIONS.get((resource, http_method), [ROOT_ADMIN])
        # If requesting user is in any of the groups that have permission to call the endpoint
        if any(group in allowed_groups for group in users_groups):
            return get_allow_policy(claims.get("sub", "unknown-user"), policy_resource, context)

        return get_deny_policy(claims.get("sub", "unknown-user"), policy_resource)

    except Exception as e:
        print(e)

    return get_deny_policy("error-user", policy_resource)

def parse_token_data(event):
    response = {'valid': False}

    auth_header = event.get("authorizationToken")
    if not auth_header:
        return response

    auth_header_list = auth_header.split(' ')

    # deny request of header isn't made out of two strings, or
    # first string isn't equal to "Bearer" (enforcing following standards,
    # but technically could be anything or could be left out completely)
    if len(auth_header_list) != 2 or auth_header_list[0] != 'Bearer' or not auth_header_list[1]:
        return response

    access_token = auth_header_list[1]
    return {
        'valid': True,
        'token': access_token
    }

def validate_token(token):
    # get the kid from the headers prior to verification
    headers = jwt.get_unverified_headers(token)
    kid = headers['kid']

    keys = get_keys()

    # search for the kid in the downloaded public keys
    key_index = -1
    for i in range(len(keys)):
        if kid == keys[i]['kid']:
            key_index = i
            break

    if key_index == -1:
        print('Public key not found in jwks.json')
        return False

    # construct the public key
    public_key = jwk.construct(keys[key_index])

    # get the last two sections of the token,
    # message and signature (encoded in base64)
    message, encoded_signature = str(token).rsplit('.', 1)

    # decode the signature
    decoded_signature = base64url_decode(encoded_signature.encode('utf-8'))

    # verify the signature
    if not public_key.verify(message.encode("utf8"), decoded_signature):
        print('Signature verification failed')
        return False

    print('Signature successfully verified')

    # since we passed the verification, we can now safely
    # use the unverified claims
    claims = jwt.get_unverified_claims(token)

    # additionally we can verify the token expiration
    if time.time() > claims['exp']:
        print('Token is expired')
        return False

    # and the Audience  (use claims['client_id'] if verifying an access token)
    if claims['client_id'] != COGNITO_APP_CLIENT_ID:
        print('Token was not issued for this audience')
        return False

    # now we can use the claims
    print(claims)
    return claims

def get_deny_policy(principalId, resource):
    print(f"Failure: returning deny policy for principalId [{principalId}]")
    return {
        "principalId": principalId,
        "policyDocument": {
            "Version": "2012-10-17",
            "Statement": [
                {
                    "Action": "execute-api:Invoke",
                    "Effect": "Deny",
                    "Resource": resource
                }
            ]
        }
    }

def get_allow_policy(principalId, resource, context):
    print(f"Success: returning allow policy for principalId [{principalId}]")
    return {
        "principalId": principalId,
        "policyDocument": {
            "Version": "2012-10-17",
            "Statement": [
                {
                    "Action": "execute-api:Invoke",
                    "Effect": "Allow",
                    "Resource": resource
                }
            ]
        },
        "context": context
    }

def parse_method_arn(arn):
    # arn looks like arn:aws:execute-api:region:account-id:api_id/stage/METHOD/resource_path
    ending = arn.split(':')[5] 
    api_id, stage, http_method, *resource_parts = ending.split('/')
    resource = '/' + '/'.join(resource_parts)
    return resource, http_method