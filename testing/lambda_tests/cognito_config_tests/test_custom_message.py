import importlib

def load_module():
    """
    Import (or reload) the Lambda after Moto has created the mocked AWS
    resources. This ensures the module"s global DynamoDB objects point at
    Moto instead of real AWS.
    """
    # DO NOT IMPORT THE FUNCTION UP TOP, IMPORT IT IN THIS FUNCTION
    module = importlib.import_module("lambdas.cognito_config.custom_message")
    return importlib.reload(module)


def test_custom_sign_up_message(aws_environment):
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
        "triggerSource": "CustomMessage_SignUp",
        "request": {
            "userAttributes": {
                "sub": "1235678-abcde-1235678-abcde",
                "email_verified": "false",
                "cognito:user_status": "UNCONFIRMED",
                "email": "test_email@gmail.com"
            },
            "codeParameter": "{####}",
            "linkParameter": "{##Click Here##}",
            "usernameParameter": None
        },
        "response": {
            "smsMessage": None,
            "emailMessage": None,
            "emailSubject": None
        }
    }

    # Act
    response = module.custom_message(event, None)

    # Assert
    assert response != None
    assert response.get("response") != None

    subject = response["response"]["emailSubject"]
    message = response["response"]["emailMessage"]

    assert subject == "Verify Your TrailCount Account"
    assert f"Hello {event['userName']}, to verify your email address please use the following code:" in message
    assert event["request"]["codeParameter"] in message

def test_custom_resend_code_message(aws_environment):
    # Arrange
    # THIS IS THE IMPORT STATEMENT - DO THIS FOR EVERY FUNCTION
    module = load_module()

    cognito = aws_environment["cognito"]

    event = {
        "version": "1",
        "region": "us-east-1",
        "userPoolId": cognito["user_pool_id"],
        "userName": "test_resend_code_user",
        "callerContext": {
            "awsSdkVersion": "aws-sdk-js-3.1010.0",
            "clientId": cognito["client_id"]
        },
        "triggerSource": "CustomMessage_ResendCode",
        "request": {
            "userAttributes": {
                "sub": "1235678-abcde-1235678-abcde",
                "email_verified": "false",
                "cognito:user_status": "UNCONFIRMED",
                "email": "test_email@gmail.com"
            },
            "codeParameter": "{####}",
            "linkParameter": "{##Click Here##}",
            "usernameParameter": None
        },
        "response": {
            "smsMessage": None,
            "emailMessage": None,
            "emailSubject": None
        }
    }

    # Act
    response = module.custom_message(event, None)

    # Assert
    assert response != None
    assert response.get("response") != None

    subject = response["response"]["emailSubject"]
    message = response["response"]["emailMessage"]

    assert subject == "Verify Your TrailCount Account (Resend)"
    assert f"Hello {event['userName']}, to verify your email address please use the following code:" in message
    assert event["request"]["codeParameter"] in message

def test_custom_forgot_password_message(aws_environment):
    # Arrange
    # THIS IS THE IMPORT STATEMENT - DO THIS FOR EVERY FUNCTION
    module = load_module()

    cognito = aws_environment["cognito"]

    event = {
        "version": "1",
        "region": "us-east-1",
        "userPoolId": cognito["user_pool_id"],
        "userName": "test_forgot_password_user",
        "callerContext": {
            "awsSdkVersion": "aws-sdk-js-3.1010.0",
            "clientId": cognito["client_id"]
        },
        "triggerSource": "CustomMessage_ForgotPassword",
        "request": {
            "userAttributes": {
                "sub": "1235678-abcde-1235678-abcde",
                "email_verified": "true",
                "cognito:user_status": "CONFIRMED",
                "email": "test_email@gmail.com"
            }, 
            "codeParameter": "{####}", 
            "linkParameter": "{##Click Here##}",
            "usernameParameter": None
        },
        "response": {
            "smsMessage": None,
            "emailMessage": None,
            "emailSubject": None
        }
    }

    # Act
    response = module.custom_message(event, None)

    # Assert
    assert response != None
    assert response.get("response") != None

    subject = response["response"]["emailSubject"]
    message = response["response"]["emailMessage"]

    assert subject == "Reset Your TrailCount Account Password"
    assert f"Hello {event['userName']}, to reset your password please use the following code:" in message
    assert event["request"]["codeParameter"] in message