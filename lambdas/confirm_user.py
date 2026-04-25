import boto3

cognito = boto3.client('cognito-idp')

def confirm_user(event, context):
    print(event)
    user_pool_id = event["userPoolId"]
    id = event["request"]["userAttributes"]["sub"]
    cognito.admin_add_user_to_group(UserPoolId=user_pool_id, Username=id, GroupName="user")

    return event