import importlib
import json

def load_module():
    """
    Import (or reload) the Lambda after Moto has created the mocked AWS
    resources. This ensures the module"s global DynamoDB objects point at
    Moto instead of real AWS.
    """
    # DO NOT IMPORT THE FUNCTION UP TOP, IMPORT IT IN THIS FUNCTION
    module = importlib.import_module("lambdas.public_api.users.users_delete")
    return importlib.reload(module)


def test_ban_user(aws_environment):
    # Arrange
    # THIS IS THE IMPORT STATEMENT - DO THIS FOR EVERY FUNCTION
    module = load_module()

    cognito = aws_environment["cognito"]

    event = {
        "body": json.dumps({
            "target_username": "trail_manager"
        }),
        "requestContext": {
            "authorizer": {
                "caller_role": "root_admin"
            }
        }
    }

    # Act
    response = module.ban_user(event, None)

    # Assert
    assert response != None
    assert response.get("statusCode") == 200

    body = json.loads(response["body"])
    assert body.get("message") == "User banned"

    user = module.cognito.admin_get_user(UserPoolId=cognito["user_pool_id"], Username="trail_manager")
    assert user["Enabled"] == False

    groups = module.cognito.admin_list_groups_for_user(UserPoolId=cognito["user_pool_id"], Username="trail_manager")["Groups"]
    assert len(groups) == 1
    assert groups[0]["GroupName"] == "banned"

def test_missing_permissions():
    # Arrange
    # THIS IS THE IMPORT STATEMENT - DO THIS FOR EVERY FUNCTION
    module = load_module()

    event = {
        "body": json.dumps({
            "target_username": "trail_manager"
        })
    }

    # Act
    response = module.ban_user(event, None)

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
            "target_username": "admin"
        }),
        "requestContext": {
            "authorizer": {
                "caller_role": "admin"
            }
        }
    }

    # Act
    response = module.ban_user(event, None)

    # Assert
    assert response != None
    assert response.get("statusCode") == 403

    body = json.loads(response["body"])
    assert body.get("error") == "Invalid permissions to ban user with role [admin] as a [admin]"

def test_missing_target_username():
    # Arrange
    # THIS IS THE IMPORT STATEMENT - DO THIS FOR EVERY FUNCTION
    module = load_module()

    event = {
        "body": json.dumps({}),
        "requestContext": {
            "authorizer": {
                "caller_role": "root_admin"
            }
        }
    }

    # Act
    response = module.ban_user(event, None)

    # Assert
    assert response != None
    assert response.get("statusCode") == 400

    body = json.loads(response["body"])
    assert body.get("error") == "Missing required field: target_username"

def test_user_not_fount():
    # Arrange
    # THIS IS THE IMPORT STATEMENT - DO THIS FOR EVERY FUNCTION
    module = load_module()

    event = {
        "body": json.dumps({
            "target_username": "testing"
        }),
        "requestContext": {
            "authorizer": {
                "caller_role": "root_admin"
            }
        }
    }

    # Act
    response = module.ban_user(event, None)

    # Assert
    assert response != None
    assert response.get("statusCode") == 400

    body = json.loads(response["body"])
    assert body.get("error") == "User with username [testing] not found"

def test_internal_server_exception(monkeypatch):
    module = load_module()

    event = {
        "body": json.dumps({
            "target_username": "user"
        }),
        "requestContext": {
            "authorizer": {
                "caller_role": "root_admin"
            }
        }
    }

    def raise_error(*args, **kwargs):
        raise RuntimeError("boom")

    monkeypatch.setattr(module.cognito, "admin_disable_user", raise_error)

    response = module.ban_user(event, None)

    assert response["statusCode"] == 500

    body = json.loads(response["body"])

    assert "Internal server error" in body.get("error")