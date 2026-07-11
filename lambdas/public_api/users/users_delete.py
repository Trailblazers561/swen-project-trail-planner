import json

from helper.helper_functions import cognito, COGNITO_USER_POOL_ID, user_groups, cors_headers

def ban_user(event, context):
    print(event)

    try:
        body = json.loads(event.get("body") or "{}")

        target_username = body.get("target_username")
        if not target_username:
            raise ValueError("Missing required field: target_username")

        caller_role = event.get("requestContext", {}).get("authorizer", {}).get("caller_role")
        if not caller_role:
            print("Error: caller role not found when needed")
            return {
                    "statusCode": 403,
                    "headers": cors_headers(),
                    "body": json.dumps({"error": "Unable to determine caller's role"})
                }

        print(f"Attempting to ban user [{target_username}] as a [{caller_role}]")
        try:
            cognito.admin_get_user(Username=target_username, UserPoolId=COGNITO_USER_POOL_ID)
        except:
            raise ValueError(f"User with username [{target_username}] not found")

        current_target_users_groups = cognito.admin_list_groups_for_user(Username=target_username, UserPoolId=COGNITO_USER_POOL_ID)["Groups"]
        current_target_user_role = max([group["GroupName"] for group in current_target_users_groups if group["GroupName"] in user_groups], key=lambda x: user_groups[x], default="user")
        if user_groups[current_target_user_role] >= user_groups[caller_role]:
            raise PermissionError(f"Invalid permissions to ban user with role [{current_target_user_role}] as a [{caller_role}]")

        cognito.admin_disable_user(UserPoolId=COGNITO_USER_POOL_ID, Username=target_username)

        for group in current_target_users_groups:
            cognito.admin_remove_user_from_group(UserPoolId=COGNITO_USER_POOL_ID, Username=target_username, GroupName=group["GroupName"])
        cognito.admin_add_user_to_group(UserPoolId=COGNITO_USER_POOL_ID, Username=target_username, GroupName="banned")

        print("Success: User banned")
        return {
            "statusCode": 200,
            "headers": cors_headers(),
            "body": json.dumps({"message": "User banned"})
        }
    except PermissionError as e:
        print(e)
        return {
            "statusCode": 403,
            "headers": cors_headers(),
            "body": json.dumps({"error": f"{str(e)}"})
        }
    except ValueError as e:
        print(e)
        return {
            "statusCode": 400,
            "headers": cors_headers(),
            "body": json.dumps({"error": f"{str(e)}"})
        }
    except Exception as e:
        print(e)
        return {
            "statusCode": 500,
            "headers": cors_headers(),
            "body": json.dumps({"error": f"Internal server error: {str(e)}"})
        }