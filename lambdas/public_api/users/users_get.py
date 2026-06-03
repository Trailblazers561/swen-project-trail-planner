import json

from helper_functions import cognito, COGNITO_USER_POOL_ID, user_groups, cors_headers

def get_users(event, context):
    print(event)

    try:
        params = event.get('queryStringParameters', {}) or {}

        target_user_role = params.get("target_user_role")
        if target_user_role and target_user_role not in user_groups:
            raise ValueError("Invalid target_user_role format")
        target_user_role = None

        max_count = int(params.get("max_count", 99))

        print(f"Attempting to retrieve user information for role [{target_user_role}] up to [{max_count}] results")
        if not target_user_role:
            paginator = cognito.get_paginator('list_users')
            user_iterator = paginator.paginate(UserPoolId=COGNITO_USER_POOL_ID)
        else:
            paginator = cognito.get_paginator('list_users_in_group')
            user_iterator = paginator.paginate(UserPoolId=COGNITO_USER_POOL_ID, GroupName=target_user_role)

        users = []
        for page in user_iterator:
            users.extend(page.get('Users', []))
            if len(users) > max_count:
                users = users[:max_count]
                break

        users_formatted = []
        attribute_names = {"sub": "user_id", "email": "email", "given_name": "first_name", "family_name": "last_name"}
        for user in users:
            if user["UserStatus"] != "CONFIRMED":
                continue
            user_formatted = {"username": user["Username"]}
            for attribute in user["Attributes"]:
                if attribute["Name"] in attribute_names.keys():
                    user_formatted[attribute_names[attribute["Name"]]] = attribute["Value"]
            groups = cognito.admin_list_groups_for_user(Username=user["Username"], UserPoolId=COGNITO_USER_POOL_ID)
            user_formatted["role"] = max([group["GroupName"] for group in groups["Groups"]], key=lambda x: user_groups[x], default="guest")
            users_formatted.append(user_formatted)

        print(f"User information successfully retrieved: {users_formatted[:3]}")
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