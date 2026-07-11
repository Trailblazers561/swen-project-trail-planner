import importlib
import json

def load_module():
    """
    Import (or reload) the Lambda after Moto has created the mocked AWS
    resources. This ensures the module"s global DynamoDB objects point at
    Moto instead of real AWS.
    """
    # DO NOT IMPORT THE FUNCTION UP TOP, IMPORT IT IN THIS FUNCTION
    module = importlib.import_module("lambdas.public_api.users.users_get")
    return importlib.reload(module)


def test_get_regular_users():
    # Arrange
    # THIS IS THE IMPORT STATEMENT - DO THIS FOR EVERY FUNCTION
    module = load_module()

    event = {
        "queryStringParameters": None,
        "multiValueQueryStringParameters": None,
    }

    # Act
    response = module.get_users(event, None)

    # Assert
    assert response != None
    assert response.get("statusCode") == 200

    users = json.loads(response["body"])
    assert users != None
    assert len(users) == 4

    usernames = {user["username"] for user in users}
    assert usernames == {"root_admin", "admin", "trail_manager", "user"}

    role_map = {"root_admin": "root_admin", "admin": "admin", "trail_manager": "trail_manager", "user": "user"}
    roles = {user["username"]: user["role"] for user in users}
    assert roles == role_map

    banned = {user["banned"] for user in users}
    assert banned == {False, False, False, False}

def test_get_limit():
    # Arrange
    # THIS IS THE IMPORT STATEMENT - DO THIS FOR EVERY FUNCTION
    module = load_module()

    event = {
        "queryStringParameters": {
            "max_count": 2
        },
        "multiValueQueryStringParameters": None,
    }

    # Act
    response = module.get_users(event, None)

    # Assert
    assert response != None
    assert response.get("statusCode") == 200

    users = json.loads(response["body"])
    assert users != None
    assert len(users) == 2

def test_get_banned_user(aws_environment):
    # Arrange
    # THIS IS THE IMPORT STATEMENT - DO THIS FOR EVERY FUNCTION
    module = load_module()

    cognito = aws_environment["cognito"]

    event = {
        "queryStringParameters": None,
        "multiValueQueryStringParameters": None,
    }

    module.cognito.admin_disable_user(UserPoolId=cognito["user_pool_id"], Username="user")
    module.cognito.admin_remove_user_from_group(UserPoolId=cognito["user_pool_id"], Username="user", GroupName="user")
    module.cognito.admin_add_user_to_group(UserPoolId=cognito["user_pool_id"], Username="user", GroupName="banned")

    # Act
    response = module.get_users(event, None)

    # Assert
    assert response != None
    assert response.get("statusCode") == 200

    users = json.loads(response["body"])
    assert users != None
    assert len(users) == 4

    usernames = {user["username"] for user in users}
    assert usernames == {"root_admin", "admin", "trail_manager", "user"}

    role_map = {"root_admin": "root_admin", "admin": "admin", "trail_manager": "trail_manager", "user": "guest"}
    roles = {user["username"]: user["role"] for user in users}
    assert roles == role_map

    user_banned = {user["banned"] for user in users if user["username"] == "user"}
    assert user_banned == {True}

def test_get_user_users():
    # Arrange
    # THIS IS THE IMPORT STATEMENT - DO THIS FOR EVERY FUNCTION
    module = load_module()

    event = {
        "queryStringParameters": {
            "target_user_role": "user"
        },
        "multiValueQueryStringParameters": None,
    }

    # Act
    response = module.get_users(event, None)

    # Assert
    assert response != None
    assert response.get("statusCode") == 200

    users = json.loads(response["body"])
    assert users != None
    assert len(users) == 4

    usernames = {user["username"] for user in users}
    assert usernames == {"root_admin", "admin", "trail_manager", "user"}

def test_get_admin_users():
    # Arrange
    # THIS IS THE IMPORT STATEMENT - DO THIS FOR EVERY FUNCTION
    module = load_module()

    event = {
        "queryStringParameters": {
            "target_user_role": "admin"
        },
        "multiValueQueryStringParameters": None,
    }

    # Act
    response = module.get_users(event, None)

    # Assert
    assert response != None
    assert response.get("statusCode") == 200

    users = json.loads(response["body"])
    assert users != None
    assert len(users) == 2

    usernames = {user["username"] for user in users}
    assert usernames == {"root_admin", "admin"}

def test_invalid_user_role():
    # Arrange
    # THIS IS THE IMPORT STATEMENT - DO THIS FOR EVERY FUNCTION
    module = load_module()

    event = {
        "queryStringParameters": {
            "target_user_role": "fail"
        },
        "multiValueQueryStringParameters": None,
    }

    # Act
    response = module.get_users(event, None)

    # Assert
    assert response != None
    assert response.get("statusCode") == 400

    body = json.loads(response["body"])
    assert body.get("error") == "Invalid target_user_role format"

def test_ignore_unconfirmed_user(aws_environment):
    # Arrange
    # THIS IS THE IMPORT STATEMENT - DO THIS FOR EVERY FUNCTION
    module = load_module()

    cognito = aws_environment["cognito"]

    event = {
        "queryStringParameters": None,
        "multiValueQueryStringParameters": None,
    }

    module.cognito.admin_create_user(
        UserPoolId=cognito["user_pool_id"],
        Username="new_user",
        UserAttributes=[
            {
                "Name": "email",
                "Value": "test_email@gmail.com",
            },
            {
                "Name": "email_verified",
                "Value": "true",
            },
        ],
        MessageAction="SUPPRESS",
    )

    # Act
    response = module.get_users(event, None)

    # Assert
    assert response != None
    assert response.get("statusCode") == 200

    users = json.loads(response["body"])
    assert users != None
    assert len(users) == 4

    usernames = {user["username"] for user in users}
    assert usernames == {"root_admin", "admin", "trail_manager", "user"}

def test_internal_server_exception(monkeypatch):
    module = load_module()

    def raise_error(*args, **kwargs):
        raise RuntimeError("boom")

    monkeypatch.setattr(module.cognito, "get_paginator", raise_error)

    response = module.get_users({}, None)

    assert response["statusCode"] == 500

    body = json.loads(response["body"])

    assert "Internal server error" in body.get("error")