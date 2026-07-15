import importlib
import json

def load_module():
    """
    Import (or reload) the Lambda after Moto has created the mocked AWS
    resources. This ensures the module"s global DynamoDB objects point at
    Moto instead of real AWS.
    """
    # DO NOT IMPORT THE FUNCTION UP TOP, IMPORT IT IN THIS FUNCTION
    module = importlib.import_module("lambdas.public_api.users.users_put")
    return importlib.reload(module)


def test_promote_user(aws_environment):
    # Arrange
    # THIS IS THE IMPORT STATEMENT - DO THIS FOR EVERY FUNCTION
    module = load_module()

    cognito = aws_environment["cognito"]

    event = {
        "body": json.dumps({
            "target_username": "user",
            "target_user_role": "trail_manager"
        }),
        "requestContext": {
            "authorizer": {
                "caller_role": "root_admin"
            }
        }
    }

    # Act
    response = module.change_user_group(event, None)

    # Assert
    assert response != None
    assert response.get("statusCode") == 200

    body = json.loads(response["body"])
    assert body.get("message") == "User groups updated"

    groups = {group["GroupName"] for group in module.cognito.admin_list_groups_for_user(UserPoolId=cognito["user_pool_id"], Username="user")["Groups"]}
    assert groups == {"trail_manager", "user"}

def test_demote_user(aws_environment):
    # Arrange
    # THIS IS THE IMPORT STATEMENT - DO THIS FOR EVERY FUNCTION
    module = load_module()

    cognito = aws_environment["cognito"]

    event = {
        "body": json.dumps({
            "target_username": "trail_manager",
            "target_user_role": "user"
        }),
        "requestContext": {
            "authorizer": {
                "caller_role": "root_admin"
            }
        }
    }

    # Act
    response = module.change_user_group(event, None)

    # Assert
    assert response != None
    assert response.get("statusCode") == 200

    body = json.loads(response["body"])
    assert body.get("message") == "User groups updated"

    groups = {group["GroupName"] for group in module.cognito.admin_list_groups_for_user(UserPoolId=cognito["user_pool_id"], Username="trail_manager")["Groups"]}
    assert groups == {"user"}

def test_unban_user(aws_environment):
    # Arrange
    # THIS IS THE IMPORT STATEMENT - DO THIS FOR EVERY FUNCTION
    module = load_module()

    cognito = aws_environment["cognito"]

    event = {
        "body": json.dumps({
            "target_username": "user",
            "target_user_role": "user"
        }),
        "requestContext": {
            "authorizer": {
                "caller_role": "root_admin"
            }
        }
    }

    module.cognito.admin_disable_user(UserPoolId=cognito["user_pool_id"], Username="user")
    module.cognito.admin_remove_user_from_group(UserPoolId=cognito["user_pool_id"], Username="user", GroupName="user")
    module.cognito.admin_add_user_to_group(UserPoolId=cognito["user_pool_id"], Username="user", GroupName="banned")

    # Act
    response = module.change_user_group(event, None)

    # Assert
    assert response != None
    assert response.get("statusCode") == 200

    body = json.loads(response["body"])
    assert body.get("message") == "User groups updated"

    groups = {group["GroupName"] for group in module.cognito.admin_list_groups_for_user(UserPoolId=cognito["user_pool_id"], Username="user")["Groups"]}
    assert groups == {"user"}

    user = module.cognito.admin_get_user(UserPoolId=cognito["user_pool_id"], Username="user")
    assert user["Enabled"] == True

def test_missing_permissions():
    # Arrange
    # THIS IS THE IMPORT STATEMENT - DO THIS FOR EVERY FUNCTION
    module = load_module()

    event = {
        "body": json.dumps({
            "target_username": "trail_manager",
            "target_user_role": "admin"
        })
    }

    # Act
    response = module.change_user_group(event, None)

    # Assert
    assert response != None
    assert response.get("statusCode") == 403

    body = json.loads(response["body"])
    assert body.get("error") == "Unable to determine caller's role"

def test_invalid_permissions():
    # Arrange
    # THIS IS THE IMPORT STATEMENT - DO THIS FOR EVERY FUNCTION
    module = load_module()

    event = {
        "body": json.dumps({
            "target_username": "trail_manager",
            "target_user_role": "admin"
        }),
        "requestContext": {
            "authorizer": {
                "caller_role": "admin"
            }
        }
    }

    # Act
    response = module.change_user_group(event, None)

    # Assert
    assert response != None
    assert response.get("statusCode") == 403

    body = json.loads(response["body"])
    assert body.get("error") == "Invalid permissions to set user to specified target_user_role"


def test_invalid_permissions_again():
    # Arrange
    # THIS IS THE IMPORT STATEMENT - DO THIS FOR EVERY FUNCTION
    module = load_module()

    event = {
        "body": json.dumps({
            "target_username": "admin",
            "target_user_role": "trail_manager"
        }),
        "requestContext": {
            "authorizer": {
                "caller_role": "admin"
            }
        }
    }

    # Act
    response = module.change_user_group(event, None)

    # Assert
    assert response != None
    assert response.get("statusCode") == 403

    body = json.loads(response["body"])
    assert body.get("error") == "Invalid permissions to change role of user with role [admin]"

def test_missing_target_username():
    # Arrange
    # THIS IS THE IMPORT STATEMENT - DO THIS FOR EVERY FUNCTION
    module = load_module()

    event = {
        "body": json.dumps({
            "target_user_role": "admin"
        }),
        "requestContext": {
            "authorizer": {
                "caller_role": "root_admin"
            }
        }
    }

    # Act
    response = module.change_user_group(event, None)

    # Assert
    assert response != None
    assert response.get("statusCode") == 400

    body = json.loads(response["body"])
    assert body.get("error") == "Missing required field: target_username"

def test_missing_target_user_role():
    # Arrange
    # THIS IS THE IMPORT STATEMENT - DO THIS FOR EVERY FUNCTION
    module = load_module()

    event = {
        "body": json.dumps({
            "target_username": "admin"
        }),
        "requestContext": {
            "authorizer": {
                "caller_role": "root_admin"
            }
        }
    }

    # Act
    response = module.change_user_group(event, None)

    # Assert
    assert response != None
    assert response.get("statusCode") == 400

    body = json.loads(response["body"])
    assert body.get("error") == "Missing required field: target_user_role"

def test_invalid_target_user_role():
    # Arrange
    # THIS IS THE IMPORT STATEMENT - DO THIS FOR EVERY FUNCTION
    module = load_module()

    event = {
        "body": json.dumps({
            "target_username": "admin",
            "target_user_role": "testing"
        }),
        "requestContext": {
            "authorizer": {
                "caller_role": "root_admin"
            }
        }
    }

    # Act
    response = module.change_user_group(event, None)

    # Assert
    assert response != None
    assert response.get("statusCode") == 400

    body = json.loads(response["body"])
    assert body.get("error") == "Invalid format for: target_user_role"

def test_user_not_fount():
    # Arrange
    # THIS IS THE IMPORT STATEMENT - DO THIS FOR EVERY FUNCTION
    module = load_module()

    event = {
        "body": json.dumps({
            "target_username": "testing",
            "target_user_role": "trail_manager"
        }),
        "requestContext": {
            "authorizer": {
                "caller_role": "root_admin"
            }
        }
    }

    # Act
    response = module.change_user_group(event, None)

    # Assert
    assert response != None
    assert response.get("statusCode") == 400

    body = json.loads(response["body"])
    assert body.get("error") == "User with username [testing] not found"

def test_internal_server_exception(monkeypatch):
    module = load_module()

    event = {
        "body": json.dumps({
            "target_username": "user",
            "target_user_role": "trail_manager"
        }),
        "requestContext": {
            "authorizer": {
                "caller_role": "root_admin"
            }
        }
    }

    def raise_error(*args, **kwargs):
        raise RuntimeError("boom")

    monkeypatch.setattr(module.cognito, "admin_list_groups_for_user", raise_error)

    response = module.change_user_group(event, None)

    assert response["statusCode"] == 500

    body = json.loads(response["body"])

    assert "Internal server error" in body.get("error")