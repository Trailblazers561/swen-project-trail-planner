import boto3

cognito = boto3.client('cognito-idp')

def remove_unverified_user(event, context):
    print(event)
    user_pool_id = event["userPoolId"]
    email = event["request"]["userAttributes"].get("email", "")
    users = cognito.list_users(UserPoolId=user_pool_id, Filter=f'email = "{email}"')["Users"]

    for user in users:
        if user["UserStatus"] == "CONFIRMED":
            print("Failing sign up because email already taken by confirmed user")
            raise Exception("Email is already taken by a verified user")

        print(f"Deleting user {user['Username']}")
        cognito.admin_delete_user(
            UserPoolId=user_pool_id,
            Username=user["Username"]
        )

    return event