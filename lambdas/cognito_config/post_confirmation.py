import boto3

cognito = boto3.client('cognito-idp')

def confirm_user(event, context):
    print(event)
    user_pool_id = event["userPoolId"]
    username = event["userName"]
    cognito.admin_add_user_to_group(UserPoolId=user_pool_id, Username=username, GroupName="user")

    return event