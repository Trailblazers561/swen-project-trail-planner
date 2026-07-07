import importlib
import pytest

def load_module():
    """
    Import (or reload) the Lambda after Moto has created the mocked AWS
    resources. This ensures the module"s global DynamoDB objects point at
    Moto instead of real AWS.
    """
    # DO NOT IMPORT THE FUNCTION UP TOP, IMPORT IT IN THIS FUNCTION
    module = importlib.import_module("lambdas.cognito_config.post_confirmation")
    return importlib.reload(module)


def test_confirm_new_user(aws_environment):
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
    event = {
        "version": "1",
        "region": "us-east-1",
        "userPoolId": cognito["user_pool_id"],
        "userName": "test_confirm_user",
        "callerContext": {
            "awsSdkVersion": "aws-sdk-js-3.1010.0",
            "clientId": cognito["client_id"]
        },
        "triggerSource": "PostConfirmation_ConfirmSignUp",
        "request": {
            "userAttributes": {
                "sub": "1235678-abcde-1235678-abcde",
                "email_verified": "true",
                "cognito:user_status": "CONFIRMED",
                "email": "test_email@gmail.com"
            }
        },
        "response": {}
    }

    module.cognito.admin_create_user(
        UserPoolId=cognito["user_pool_id"],
        Username="test_confirm_user",
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
        Username="test_confirm_user",
        Password="password",
        Permanent=True,
    )

    user = [user for user in module.cognito.list_users(UserPoolId=cognito["user_pool_id"])["Users"] if user["Username"] == "test_confirm_user"]
    # The Confirmed User Was Sucessfully Added
    assert len(user) == 1
    assert user[0].get("UserStatus") == "CONFIRMED"

    # Act
    response = module.confirm_user(event, None)

    # Assert
    assert response == event

    groups = [group["GroupName"] for group in module.cognito.admin_list_groups_for_user(Username="test_confirm_user", UserPoolId=cognito["user_pool_id"])["Groups"]]
    print(groups)
    # User Was Put Into "user" User Group
    assert groups == ["user"]