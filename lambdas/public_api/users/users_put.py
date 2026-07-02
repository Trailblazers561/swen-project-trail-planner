import json

from helper.helper_functions import cognito, COGNITO_USER_POOL_ID, user_groups, cors_headers

def change_user_group(event, context):
    print(event)

    try:
        body = json.loads(event.get("body") or "{}")

        target_username = body.get("target_username")
        target_user_role = body.get("target_user_role")
        if not target_username:
            raise ValueError("Missing required field: target_username")
        if not target_user_role:
            raise ValueError("Missing required field: target_user_role")

        if target_user_role not in user_groups:
            raise ValueError("Invalid format for: target_user_role")

        caller_role = event.get("requestContext", {}).get("authorizer", {}).get("caller_role")
        if not caller_role:
            print("Error: caller role not found when needed")
            return {
                    "statusCode": 400,
                    "headers": cors_headers(),
                    "body": json.dumps({"error": "Unable to determine caller's role"})
                }

        if user_groups[target_user_role] >= user_groups[caller_role]:
            raise PermissionError("Invalid permissions to set user to specified target_user_role")

        print(f"Attempting to update user groups for user [{target_username}] to role [{target_user_role}] as a [{caller_role}]")
        try:
            user = cognito.admin_get_user(Username=target_username, UserPoolId=COGNITO_USER_POOL_ID)
        except Exception:
            raise ValueError(f"User with username [{target_username}] not found")

        if not user["Enabled"]:
            print("User is banned, unbanning them")
            cognito.admin_enable_user(Username=target_username, UserPoolId=COGNITO_USER_POOL_ID)

        end_target_groups = [group for group in user_groups.keys() if user_groups[group] <= user_groups[target_user_role]]
        current_target_users_groups = cognito.admin_list_groups_for_user(Username=target_username, UserPoolId=COGNITO_USER_POOL_ID)["Groups"]
        current_target_user_role = max([group["GroupName"] for group in current_target_users_groups if group["GroupName"] in user_groups], key=lambda x: user_groups[x], default="user")
        if user_groups[current_target_user_role] >= user_groups[caller_role]:
            raise PermissionError("Invalid permissions to set user to specified target_user_role")
        for group in current_target_users_groups:
            if group["GroupName"] in end_target_groups:
                end_target_groups.remove(group["GroupName"])
            else:
                cognito.admin_remove_user_from_group(UserPoolId=COGNITO_USER_POOL_ID, Username=target_username, GroupName=group["GroupName"])
        for group in end_target_groups:
            cognito.admin_add_user_to_group(UserPoolId=COGNITO_USER_POOL_ID, Username=target_username, GroupName=group)

        print("Success: User groups updated")
        return {
            "statusCode": 200,
            "headers": cors_headers(),
            "body": json.dumps({"message": "User groups updated"})
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