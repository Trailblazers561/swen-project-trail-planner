import boto3
import json
import os


COGNITO_USER_POOL_ID = os.environ.get("COGNITO_USER_POOL_ID")

ROOT_ADMIN = os.environ.get("ROOT_ADMIN", "local_trailplanner_root_admin")
ADMIN = os.environ.get("ADMIN", "local_trailplanner_admin")
TRAIL_MANAGER = os.environ.get("TRAIL_MANAGER", "local_trailplanner_trail_manager")
USER = os.environ.get("USER", "local_trailplanner_user")

cognito = boto3.client('cognito-idp')

user_groups = {"user": 0, "trail_manager": 1, "admin": 2, "root_admin": 3}
group_names = {"user": USER, "trail_manager": TRAIL_MANAGER, "admin": ADMIN, "root_admin": ROOT_ADMIN}
group_names_reversed = {USER: "user", TRAIL_MANAGER: "trail_manager", ADMIN: "admin", ROOT_ADMIN: "root_admin"}

# GET /user command
def get_users(event, context):
    print(event)

    try:
        params = event.get('queryStringParameters', {}) or {}

        target_user_role = params.get("target_user_role")
        if target_user_role and not user_groups.get(target_user_role):
            raise ValueError("Invalid target_user_role format")
        target_user_role = None

        max_count = int(params.get("max_count", 99))

        print(f"Attempting to retrieve user information for role [{target_user_role}] up to [{max_count}] results")
        if not target_user_role:
            paginator = cognito.get_paginator('list_users')
            user_iterator = paginator.paginate(UserPoolId=COGNITO_USER_POOL_ID)
        else:
            paginator = cognito.get_paginator('list_users_in_group')
            user_iterator = paginator.paginate(UserPoolId=COGNITO_USER_POOL_ID, GroupName=group_names[target_user_role])

        users = []
        for page in user_iterator:
            users.extend(page.get('Users', []))
            if len(users) > max_count:
                users = users[:max_count]
                break

        users_formatted = []
        attribute_names = {"sub": "user_id", "email": "email", "given_name": "first_name", "family_name": "last_name", "preferred_username": "username"}
        for user in users:
            user_formatted = {"username": user["Username"]}
            for attribute in user["Attributes"]:
                if attribute["Name"] in attribute_names.keys():
                    user_formatted[attribute_names[attribute["Name"]]] = attribute["Value"]
            groups = cognito.admin_list_groups_for_user(Username=user["Username"], UserPoolId=COGNITO_USER_POOL_ID)
            user_formatted["role"] = max([group_names_reversed[group["GroupName"]] for group in groups["Groups"]], key=lambda x: user_groups[x], default="guest")
            users_formatted.append(user_formatted)

        print(f"User information successfully retrieved: {user_formatted[:3]}")
        return {
            "statusCode": 200,
            "headers": cors_headers(),
            "body": json.dumps(users_formatted)
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

# POST /user command
def change_user_group(event, context):
    print(event)

    try:
        body = json.loads(event.get("body") or "{}")

        target_user_id = body.get("target_user_id")
        target_user_role = body.get("target_user_role")
        if not target_user_id:
            raise ValueError("Missing required field: target_username")
        if not target_user_role:
            raise ValueError("Missing required field: target_user_role")

        if not user_groups.get(target_user_role):
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

        print(f"Attempting to update user groups for user [{target_user_id}] to role [{target_user_role}] as a [{caller_role}]")

        end_target_groups = [group_names[group] for group in user_groups.keys() if user_groups[group] <= user_groups[target_user_role]]
        current_target_users_groups = cognito.admin_list_groups_for_user(Username=target_user_id, UserPoolId=COGNITO_USER_POOL_ID)["Groups"]
        current_target_user_role = max([group_names_reversed[group["GroupName"]] for group in current_target_users_groups], key=lambda x: user_groups[x], default="guest")
        if user_groups[current_target_user_role] >= user_groups[caller_role]:
            raise PermissionError("Invalid permissions to set user to specified target_user_role")
        for group in current_target_users_groups:
            if group["GroupName"] in end_target_groups:
                end_target_groups.remove(group["GroupName"])
            else:
                cognito.admin_remove_user_from_group(UserPoolId=COGNITO_USER_POOL_ID, Username=target_user_id, GroupName=group["GroupName"])
        for group in end_target_groups:
            cognito.admin_add_user_to_group(UserPoolId=COGNITO_USER_POOL_ID, Username=target_user_id, GroupName=group)

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

def cors_headers():
    return {
        "Access-Control-Allow-Origin": "*",
        "Access-Control-Allow-Methods": "GET,POST,PUT,DELETE,OPTIONS",
        "Access-Control-Allow-Headers": "Content-Type,Authorization"
    }