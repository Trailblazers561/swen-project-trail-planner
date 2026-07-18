import importlib

def load_module():
    """
    Import (or reload) the Lambda after Moto has created the mocked AWS
    resources. This ensures the module's global DynamoDB objects point at
    Moto instead of real AWS.
    """
    # DO NOT IMPORT THE FUNCTION UP TOP, IMPORT IT IN THIS FUNCTION
    module = importlib.import_module("lambdas.lambda_authorizer.lambda_authorizer")
    return importlib.reload(module)

def test_parse_token_valid():
    # Arrange
    module = load_module()

    event = {
        "authorizationToken": "Bearer abc123"
    }

    # Act
    result = module.parse_token_data(event)

    # Assert
    assert result["valid"] is True
    assert result["token"] == "abc123"
    assert result == {"valid": True, "token": "abc123",}

def test_parse_token_missing_header():
    # Arrange
    module = load_module()

    event = {}

    # Act
    result = module.parse_token_data(event)

    # Assert
    assert result == {"valid": False}

def test_parse_token_empty_header():
    # Arrange
    module = load_module()

    event = {
        "authorizationToken": ""
    }

    # Act
    result = module.parse_token_data(event)

    # Assert
    assert result["valid"] is False

def test_parse_token_wrong_prefix():
    # Arrange
    module = load_module()

    event = {
        "authorizationToken": "Basic abc"
    }

    # Act
    result = module.parse_token_data(event)

    # Assert
    assert result["valid"] is False

def test_parse_token_missing_token():
    # Arrange
    module = load_module()

    event = {
        "authorizationToken": "Bearer "
    }

    # Act
    result = module.parse_token_data(event)

    # Assert
    assert result["valid"] is False

def test_parse_token_three_parts():
    # Arrange
    module = load_module()

    event = {
        "authorizationToken": "Bearer abc def"
    }

    # Act
    result = module.parse_token_data(event)

    # Assert
    assert result["valid"] is False

def test_parse_method_arn():
    # Arrange
    module = load_module()

    arn = "arn:aws:execute-api:us-east-1:123:api/dev/GET/areas"

    # Act
    resource, method = module.parse_method_arn(arn)

    # Assert
    assert resource == "/areas"
    assert method == "GET"

def test_parse_method_arn_nested():
    # Arrange
    module = load_module()

    arn = "arn:aws:execute-api:us-east-1:123:api/dev/PUT/trail/data"

    # Act
    resource, method = module.parse_method_arn(arn)

    # Assert
    assert resource == "/trail/data"
    assert method == "PUT"

def test_get_allow_policy():
    # Arrange
    module = load_module()

    # Act
    result = module.get_allow_policy(
        "user1",
        "resource",
        {"caller_role": "admin"}
    )

    # Assert
    assert result["principalId"] == "user1"
    assert result["policyDocument"]["Statement"][0]["Effect"] == "Allow"
    assert result["context"]["caller_role"] == "admin"

def test_get_deny_policy():
    # Arrange
    module = load_module()

    # Act
    result = module.get_deny_policy(
        "user1",
        "resource"
    )

    # Assert
    assert result["principalId"] == "user1"
    assert result["policyDocument"]["Statement"][0]["Effect"] == "Deny"

def test_handler_guest_allowed(monkeypatch):
    # Arrange
    module = load_module()

    event = {
        "methodArn": "arn:aws:execute-api:us-east-1:1:api/dev/GET/heatmap"
    }

    # Act
    result = module.handler(event, None)

    # Assert
    assert result["policyDocument"]["Statement"][0]["Effect"] == "Allow"

def test_handler_guest_denied():
    # Arrange
    module = load_module()

    event = {
        "methodArn": "arn:aws:execute-api:us-east-1:1:api/dev/GET/users"
    }

    # Act
    result = module.handler(event, None)

    # Assert
    assert result["policyDocument"]["Statement"][0]["Effect"] == "Deny"