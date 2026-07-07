import importlib
import pytest

def load_module():
    """
    Import (or reload) the Lambda after Moto has created the mocked AWS
    resources. This ensures the module"s global DynamoDB objects point at
    Moto instead of real AWS.
    """
    # DO NOT IMPORT THE FUNCTION UP TOP, IMPORT IT IN THIS FUNCTION
    module = importlib.import_module("lambdas.cognito_config.pre_sign_up")
    return importlib.reload(module)


def test_sign_up_new_user(aws_environment):
    # Arrange
    # THIS IS THE IMPORT STATEMENT - DO THIS FOR EVERY FUNCTION
    module = load_module()

    cognito = aws_environment["cognito"]

    event = {
        "version": "1",
        "region": "us-east-1",
        "userPoolId": cognito["user_pool_id"],
        "userName": "test_sign_up_user",
        "callerContext": {
            "awsSdkVersion": "aws-sdk-js-3.1010.0",
            "clientId": cognito["client_id"]
        },
        "triggerSource": "PreSignUp_SignUp",
        "request": {
            "userAttributes": {
                "email": "test_email@gmail.com"
            },
            "validationData": None
        }, "response": {
            "autoConfirmUser": False,
            "autoVerifyEmail": False,
            "autoVerifyPhone": False
        }
    }

    # Act
    response = module.remove_unverified_user(event, None)

    # Assert
    assert response == event

    usernames = {user["Username"] for user in module.cognito.list_users(UserPoolId=cognito["user_pool_id"])["Users"]}
    # None Of The Original Four Users Were Removed
    assert set(usernames) == {"root_admin", "admin", "trail_manager", "user"}

def test_sign_up_existing_user_unconfirmed(aws_environment):
    # Arrange
    # THIS IS THE IMPORT STATEMENT - DO THIS FOR EVERY FUNCTION
    module = load_module()

    cognito = aws_environment["cognito"]

    event = {
        "version": "1",
        "region": "us-east-1",
        "userPoolId": cognito["user_pool_id"],
        "userName": "test_new_unconfirmed_user",
        "callerContext": {
            "awsSdkVersion": "aws-sdk-js-3.1010.0",
            "clientId": cognito["client_id"]
        },
        "triggerSource": "PreSignUp_SignUp",
        "request": {
            "userAttributes": {
                "email": "test_email@gmail.com"
            },
            "validationData": None
        }, "response": {
            "autoConfirmUser": False,
            "autoVerifyEmail": False,
            "autoVerifyPhone": False
        }
    }

    module.cognito.sign_up(
        ClientId=cognito["client_id"],
        Username="test_existing_unconfirmed_user",
        Password="password",
        UserAttributes=[
            {
                "Name": "email",
                "Value": "test_email@gmail.com",
            },
        ],
    )

    usernames = {user["Username"] for user in module.cognito.list_users(UserPoolId=cognito["user_pool_id"])["Users"]}
    # The Unconfirmed User Was Sucessfully Added
    assert set(usernames) == {"root_admin", "admin", "trail_manager", "user", "test_existing_unconfirmed_user"}

    # Act
    response = module.remove_unverified_user(event, None)

    # Assert
    assert response == event

    usernames = {user["Username"] for user in module.cognito.list_users(UserPoolId=cognito["user_pool_id"])["Users"]}
    # The Unconfirmed User Was Removed To Prepare For The New User
    assert set(usernames) == {"root_admin", "admin", "trail_manager", "user"}

def test_sign_up_existing_user_confirmed(aws_environment):
    # Arrange
    # THIS IS THE IMPORT STATEMENT - DO THIS FOR EVERY FUNCTION
    module = load_module()

    cognito = aws_environment["cognito"]

    event = {
        "version": "1",
        "region": "us-east-1",
        "userPoolId": cognito["user_pool_id"],
        "userName": "test_new_confirmed_user",
        "callerContext": {
            "awsSdkVersion": "aws-sdk-js-3.1010.0",
            "clientId": cognito["client_id"]
        },
        "triggerSource": "PreSignUp_SignUp",
        "request": {
            "userAttributes": {
                "email": "test_email@gmail.com"
            },
            "validationData": None
        }, "response": {
            "autoConfirmUser": False,
            "autoVerifyEmail": False,
            "autoVerifyPhone": False
        }
    }

    module.cognito.admin_create_user(
        UserPoolId=cognito["user_pool_id"],
        Username="test_existing_confirmed_user",
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

    module.cognito.admin_set_user_password(
        UserPoolId=cognito["user_pool_id"],
        Username="test_existing_confirmed_user",
        Password="password",
        Permanent=True,
    )

    user = [user for user in module.cognito.list_users(UserPoolId=cognito["user_pool_id"])["Users"] if user["Username"] == "test_existing_confirmed_user"]
    # The Confirmed User Was Sucessfully Added
    assert len(user) == 1
    assert user[0].get("UserStatus") == "CONFIRMED"

    with pytest.raises(Exception, match="Email is already taken by a verified user"):
        module.remove_unverified_user(event, None)