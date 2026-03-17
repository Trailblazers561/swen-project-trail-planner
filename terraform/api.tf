# API Gateway (REST API)
resource "aws_api_gateway_rest_api" "api" {
  body = jsonencode({
    openapi = "3.0.1"
    info = {
      title   = "${var.deploy_env}_${var.default_name}_api"
      version = "1.0"
    }
  })
  name = "${var.deploy_env}_${var.default_name}_api"
}

# /trail_data Resource
resource "aws_api_gateway_resource" "trail_data" {
  path_part   = "trail_data"
  parent_id   = aws_api_gateway_rest_api.api.root_resource_id
  rest_api_id = aws_api_gateway_rest_api.api.id
}

# CORS (OPTIONS) for /trail_data
resource "aws_api_gateway_method" "trail_data_options" {
  rest_api_id   = aws_api_gateway_rest_api.api.id
  resource_id   = aws_api_gateway_resource.trail_data.id
  http_method   = "OPTIONS"
  authorization = "NONE"
}

resource "aws_api_gateway_integration" "trail_data_options_integration" {
  rest_api_id = aws_api_gateway_rest_api.api.id
  resource_id = aws_api_gateway_resource.trail_data.id
  http_method = aws_api_gateway_method.trail_data_options.http_method
  type        = "MOCK"

  request_templates = {
    "application/json" = "{\"statusCode\": 200}"
  }
}

resource "aws_api_gateway_method_response" "trail_data_options_response" {
  rest_api_id = aws_api_gateway_rest_api.api.id
  resource_id = aws_api_gateway_resource.trail_data.id
  http_method = aws_api_gateway_method.trail_data_options.http_method
  status_code = "200"

  response_parameters = {
    "method.response.header.Access-Control-Allow-Headers"      = true
    "method.response.header.Access-Control-Allow-Methods"      = true
    "method.response.header.Access-Control-Allow-Origin"       = true
    "method.response.header.Access-Control-Allow-Credentials"  = true
  }
}

resource "aws_api_gateway_integration_response" "trail_data_options_integration_response" {
  rest_api_id = aws_api_gateway_rest_api.api.id
  resource_id = aws_api_gateway_resource.trail_data.id
  http_method = aws_api_gateway_method.trail_data_options.http_method
  status_code = "200"

  response_parameters = {
    "method.response.header.Access-Control-Allow-Headers"      = "'Content-Type,X-Amz-Date,Authorization,X-Api-Key,X-Amz-Security-Token'"
    "method.response.header.Access-Control-Allow-Methods"      = "'GET,POST,PUT,OPTIONS'"
    "method.response.header.Access-Control-Allow-Origin"       = "'*'"
    "method.response.header.Access-Control-Allow-Credentials"  = "'true'"
  }

  depends_on = [
    aws_api_gateway_integration.trail_data_options_integration,
    aws_api_gateway_method_response.trail_data_options_response
  ]
}

# /devices Resource (plural - for device POST requests)
resource "aws_api_gateway_resource" "devices" {
  path_part   = "devices"
  parent_id   = aws_api_gateway_rest_api.api.root_resource_id
  rest_api_id = aws_api_gateway_rest_api.api.id
}

# CORS (OPTIONS) for /devices
resource "aws_api_gateway_method" "devices_options" {
  rest_api_id   = aws_api_gateway_rest_api.api.id
  resource_id   = aws_api_gateway_resource.devices.id
  http_method   = "OPTIONS"
  authorization = "NONE"
}

resource "aws_api_gateway_integration" "devices_options_integration" {
  rest_api_id = aws_api_gateway_rest_api.api.id
  resource_id = aws_api_gateway_resource.devices.id
  http_method = aws_api_gateway_method.devices_options.http_method
  type        = "MOCK"

  request_templates = {
    "application/json" = "{\"statusCode\": 200}"
  }
}

resource "aws_api_gateway_method_response" "devices_options_response" {
  rest_api_id = aws_api_gateway_rest_api.api.id
  resource_id = aws_api_gateway_resource.devices.id
  http_method = aws_api_gateway_method.devices_options.http_method
  status_code = "200"

  response_parameters = {
    "method.response.header.Access-Control-Allow-Headers"      = true
    "method.response.header.Access-Control-Allow-Methods"      = true
    "method.response.header.Access-Control-Allow-Origin"       = true
    "method.response.header.Access-Control-Allow-Credentials"  = true
  }
}

resource "aws_api_gateway_integration_response" "devices_options_integration_response" {
  rest_api_id = aws_api_gateway_rest_api.api.id
  resource_id = aws_api_gateway_resource.devices.id
  http_method = aws_api_gateway_method.devices_options.http_method
  status_code = "200"

  response_parameters = {
    "method.response.header.Access-Control-Allow-Headers"      = "'Content-Type,X-Amz-Date,Authorization,X-Api-Key,X-Amz-Security-Token'"
    "method.response.header.Access-Control-Allow-Methods"      = "'POST,OPTIONS'"
    "method.response.header.Access-Control-Allow-Origin"       = "'*'"
    "method.response.header.Access-Control-Allow-Credentials"  = "'true'"
  }

  depends_on = [
    aws_api_gateway_integration.devices_options_integration,
    aws_api_gateway_method_response.devices_options_response
  ]
}

# POST /devices -> Lambda: upload_device_data (requires API key, no Cognito auth)
resource "aws_api_gateway_method" "devices_post" {
  rest_api_id   = aws_api_gateway_rest_api.api.id
  resource_id   = aws_api_gateway_resource.devices.id
  http_method   = "POST"
  authorization = "NONE"
  api_key_required = true
}

resource "aws_api_gateway_integration" "devices_post_integration" {
  rest_api_id             = aws_api_gateway_rest_api.api.id
  resource_id             = aws_api_gateway_resource.devices.id
  http_method             = aws_api_gateway_method.devices_post.http_method
  integration_http_method = "POST"
  type                    = "AWS_PROXY"
  uri                     = aws_lambda_function.upload_device_data.invoke_arn
}

# POST /trail_data -> Lambda: upload_trail_data
resource "aws_api_gateway_method" "trail_data_post" {
  rest_api_id   = aws_api_gateway_rest_api.api.id
  resource_id   = aws_api_gateway_resource.trail_data.id
  http_method   = "POST"
  authorization = var.authorization_type
  authorizer_id = aws_api_gateway_authorizer.cognito_authorizer.id
}

resource "aws_api_gateway_integration" "trail_data_post_integration" {
  rest_api_id             = aws_api_gateway_rest_api.api.id
  resource_id             = aws_api_gateway_resource.trail_data.id
  http_method             = aws_api_gateway_method.trail_data_post.http_method
  integration_http_method = "POST"
  type                    = "AWS_PROXY"
  uri                     = aws_lambda_function.upload_trail_data.invoke_arn
}

# GET /trail_data -> Lambda: get_trail_data
resource "aws_api_gateway_method" "trail_data_get" {
  rest_api_id   = aws_api_gateway_rest_api.api.id
  resource_id   = aws_api_gateway_resource.trail_data.id
  http_method   = "GET"
  authorization = var.authorization_type
  authorizer_id = aws_api_gateway_authorizer.cognito_authorizer.id
}

resource "aws_api_gateway_integration" "trail_data_get_integration" {
  rest_api_id             = aws_api_gateway_rest_api.api.id
  resource_id             = aws_api_gateway_resource.trail_data.id
  http_method             = aws_api_gateway_method.trail_data_get.http_method
  integration_http_method = "POST"
  type                    = "AWS_PROXY"
  uri                     = aws_lambda_function.get_trail_data.invoke_arn
}

# /trail_metadata Resource
resource "aws_api_gateway_resource" "trail_metadata" {
  path_part   = "trail_metadata"
  parent_id   = aws_api_gateway_rest_api.api.root_resource_id
  rest_api_id = aws_api_gateway_rest_api.api.id
}

# CORS (OPTIONS) for /trail_metadata
resource "aws_api_gateway_method" "trail_metadata_options" {
  rest_api_id   = aws_api_gateway_rest_api.api.id
  resource_id   = aws_api_gateway_resource.trail_metadata.id
  http_method   = "OPTIONS"
  authorization = "NONE"
}

resource "aws_api_gateway_integration" "trail_metadata_options_integration" {
  rest_api_id = aws_api_gateway_rest_api.api.id
  resource_id = aws_api_gateway_resource.trail_metadata.id
  http_method = aws_api_gateway_method.trail_metadata_options.http_method
  type        = "MOCK"
  request_templates = {
    "application/json" = "{\"statusCode\": 200}"
  }
}

resource "aws_api_gateway_method_response" "trail_metadata_options_response" {
  rest_api_id = aws_api_gateway_rest_api.api.id
  resource_id = aws_api_gateway_resource.trail_metadata.id
  http_method = aws_api_gateway_method.trail_metadata_options.http_method
  status_code = "200"
  response_parameters = {
    "method.response.header.Access-Control-Allow-Headers"      = true
    "method.response.header.Access-Control-Allow-Methods"      = true
    "method.response.header.Access-Control-Allow-Origin"       = true
    "method.response.header.Access-Control-Allow-Credentials"  = true
  }
}

resource "aws_api_gateway_integration_response" "trail_metadata_options_integration_response" {
  rest_api_id = aws_api_gateway_rest_api.api.id
  resource_id = aws_api_gateway_resource.trail_metadata.id
  http_method = aws_api_gateway_method.trail_metadata_options.http_method
  status_code = "200"
  response_parameters = {
    "method.response.header.Access-Control-Allow-Headers"      = "'Content-Type,X-Amz-Date,Authorization,X-Api-Key,X-Amz-Security-Token'"
    "method.response.header.Access-Control-Allow-Methods"      = "'GET,POST,PUT,DELETE,OPTIONS'"
    "method.response.header.Access-Control-Allow-Origin"       = "'*'"
    "method.response.header.Access-Control-Allow-Credentials"  = "'true'"
  }
  depends_on = [
    aws_api_gateway_integration.trail_metadata_options_integration,
    aws_api_gateway_method_response.trail_metadata_options_response
  ]
}

# GET /trail_metadata
resource "aws_api_gateway_method" "trail_metadata_get" {
  rest_api_id   = aws_api_gateway_rest_api.api.id
  resource_id   = aws_api_gateway_resource.trail_metadata.id
  http_method   = "GET"
  authorization = var.authorization_type
  authorizer_id = aws_api_gateway_authorizer.cognito_authorizer.id
}

resource "aws_api_gateway_integration" "trail_metadata_get_integration" {
  rest_api_id             = aws_api_gateway_rest_api.api.id
  resource_id             = aws_api_gateway_resource.trail_metadata.id
  http_method             = aws_api_gateway_method.trail_metadata_get.http_method
  integration_http_method = "POST"
  type                    = "AWS_PROXY"
  uri                     = aws_lambda_function.get_trail_metadata.invoke_arn
}

# PUT /trail_metadata
resource "aws_api_gateway_method" "trail_metadata_put" {
  rest_api_id   = aws_api_gateway_rest_api.api.id
  resource_id   = aws_api_gateway_resource.trail_metadata.id
  http_method   = "PUT"
  authorization = var.authorization_type
  authorizer_id = aws_api_gateway_authorizer.cognito_authorizer.id
}

resource "aws_api_gateway_integration" "trail_metadata_put_integration" {
  rest_api_id             = aws_api_gateway_rest_api.api.id
  resource_id             = aws_api_gateway_resource.trail_metadata.id
  http_method             = aws_api_gateway_method.trail_metadata_put.http_method
  integration_http_method = "POST"
  type                    = "AWS_PROXY"
  uri                     = aws_lambda_function.update_trail_metadata.invoke_arn
}

# POST /trail_metadata (create new trail)
resource "aws_api_gateway_method" "trail_metadata_post" {
  rest_api_id   = aws_api_gateway_rest_api.api.id
  resource_id   = aws_api_gateway_resource.trail_metadata.id
  http_method   = "POST"
  authorization = var.authorization_type
  authorizer_id = aws_api_gateway_authorizer.cognito_authorizer.id
}

resource "aws_api_gateway_integration" "trail_metadata_post_integration" {
  rest_api_id             = aws_api_gateway_rest_api.api.id
  resource_id             = aws_api_gateway_resource.trail_metadata.id
  http_method             = aws_api_gateway_method.trail_metadata_post.http_method
  integration_http_method = "POST"
  type                    = "AWS_PROXY"
  uri                     = aws_lambda_function.create_trail.invoke_arn
}

# DELETE /trail_metadata
resource "aws_api_gateway_method" "trail_metadata_delete" {
  rest_api_id   = aws_api_gateway_rest_api.api.id
  resource_id   = aws_api_gateway_resource.trail_metadata.id
  http_method   = "DELETE"
  authorization = var.authorization_type
  authorizer_id = aws_api_gateway_authorizer.cognito_authorizer.id
}

resource "aws_api_gateway_integration" "trail_metadata_delete_integration" {
  rest_api_id             = aws_api_gateway_rest_api.api.id
  resource_id             = aws_api_gateway_resource.trail_metadata.id
  http_method             = aws_api_gateway_method.trail_metadata_delete.http_method
  integration_http_method = "POST"
  type                    = "AWS_PROXY"
  uri                     = aws_lambda_function.delete_trail.invoke_arn
}

# /device_metadata Resource
resource "aws_api_gateway_resource" "device_metadata" {
  path_part   = "device_metadata"
  parent_id   = aws_api_gateway_rest_api.api.root_resource_id
  rest_api_id = aws_api_gateway_rest_api.api.id
}

# CORS (OPTIONS) for /device_metadata
resource "aws_api_gateway_method" "device_metadata_options" {
  rest_api_id   = aws_api_gateway_rest_api.api.id
  resource_id   = aws_api_gateway_resource.device_metadata.id
  http_method   = "OPTIONS"
  authorization = "NONE"
}

resource "aws_api_gateway_integration" "device_metadata_options_integration" {
  rest_api_id = aws_api_gateway_rest_api.api.id
  resource_id = aws_api_gateway_resource.device_metadata.id
  http_method = aws_api_gateway_method.device_metadata_options.http_method
  type        = "MOCK"
  request_templates = {
    "application/json" = "{\"statusCode\": 200}"
  }
}

resource "aws_api_gateway_method_response" "device_metadata_options_response" {
  rest_api_id = aws_api_gateway_rest_api.api.id
  resource_id = aws_api_gateway_resource.device_metadata.id
  http_method = aws_api_gateway_method.device_metadata_options.http_method
  status_code = "200"
  response_parameters = {
    "method.response.header.Access-Control-Allow-Headers"      = true
    "method.response.header.Access-Control-Allow-Methods"      = true
    "method.response.header.Access-Control-Allow-Origin"       = true
    "method.response.header.Access-Control-Allow-Credentials"  = true
  }
}

resource "aws_api_gateway_integration_response" "device_metadata_options_integration_response" {
  rest_api_id = aws_api_gateway_rest_api.api.id
  resource_id = aws_api_gateway_resource.device_metadata.id
  http_method = aws_api_gateway_method.device_metadata_options.http_method
  status_code = "200"
  response_parameters = {
    "method.response.header.Access-Control-Allow-Headers"      = "'Content-Type,X-Amz-Date,Authorization,X-Api-Key,X-Amz-Security-Token'"
    "method.response.header.Access-Control-Allow-Methods"      = "'GET,POST,PUT,DELETE,OPTIONS'"
    "method.response.header.Access-Control-Allow-Origin"       = "'*'"
    "method.response.header.Access-Control-Allow-Credentials"  = "'true'"
  }
  depends_on = [
    aws_api_gateway_integration.device_metadata_options_integration,
    aws_api_gateway_method_response.device_metadata_options_response
  ]
}

# GET /device_metadata
resource "aws_api_gateway_method" "device_metadata_get" {
  rest_api_id   = aws_api_gateway_rest_api.api.id
  resource_id   = aws_api_gateway_resource.device_metadata.id
  http_method   = "GET"
  authorization = var.authorization_type
  authorizer_id = aws_api_gateway_authorizer.cognito_authorizer.id
}

resource "aws_api_gateway_integration" "device_metadata_get_integration" {
  rest_api_id             = aws_api_gateway_rest_api.api.id
  resource_id             = aws_api_gateway_resource.device_metadata.id
  http_method             = aws_api_gateway_method.device_metadata_get.http_method
  integration_http_method = "POST"
  type                    = "AWS_PROXY"
  uri                     = aws_lambda_function.get_device_metadata.invoke_arn
}

# PUT /device_metadata
resource "aws_api_gateway_method" "device_metadata_put" {
  rest_api_id   = aws_api_gateway_rest_api.api.id
  resource_id   = aws_api_gateway_resource.device_metadata.id
  http_method   = "PUT"
  authorization = var.authorization_type
  authorizer_id = aws_api_gateway_authorizer.cognito_authorizer.id
}

resource "aws_api_gateway_integration" "device_metadata_put_integration" {
  rest_api_id             = aws_api_gateway_rest_api.api.id
  resource_id             = aws_api_gateway_resource.device_metadata.id
  http_method             = aws_api_gateway_method.device_metadata_put.http_method
  integration_http_method = "POST"
  type                    = "AWS_PROXY"
  uri                     = aws_lambda_function.update_device_trail_association.invoke_arn
}

# /trail_groups Resource
resource "aws_api_gateway_resource" "trail_groups" {
  path_part   = "trail_groups"
  parent_id   = aws_api_gateway_rest_api.api.root_resource_id
  rest_api_id = aws_api_gateway_rest_api.api.id
}

# CORS (OPTIONS) for /trail_groups
resource "aws_api_gateway_method" "trail_groups_options" {
  rest_api_id   = aws_api_gateway_rest_api.api.id
  resource_id   = aws_api_gateway_resource.trail_groups.id
  http_method   = "OPTIONS"
  authorization = "NONE"
}

resource "aws_api_gateway_integration" "trail_groups_options_integration" {
  rest_api_id = aws_api_gateway_rest_api.api.id
  resource_id = aws_api_gateway_resource.trail_groups.id
  http_method = aws_api_gateway_method.trail_groups_options.http_method
  type        = "MOCK"
  request_templates = {
    "application/json" = "{\"statusCode\": 200}"
  }
}

resource "aws_api_gateway_method_response" "trail_groups_options_response" {
  rest_api_id = aws_api_gateway_rest_api.api.id
  resource_id = aws_api_gateway_resource.trail_groups.id
  http_method = aws_api_gateway_method.trail_groups_options.http_method
  status_code = "200"
  response_parameters = {
    "method.response.header.Access-Control-Allow-Headers"      = true
    "method.response.header.Access-Control-Allow-Methods"      = true
    "method.response.header.Access-Control-Allow-Origin"       = true
    "method.response.header.Access-Control-Allow-Credentials"  = true
  }
}

resource "aws_api_gateway_integration_response" "trail_groups_options_integration_response" {
  rest_api_id = aws_api_gateway_rest_api.api.id
  resource_id = aws_api_gateway_resource.trail_groups.id
  http_method = aws_api_gateway_method.trail_groups_options.http_method
  status_code = "200"
  response_parameters = {
    "method.response.header.Access-Control-Allow-Headers"      = "'Content-Type,X-Amz-Date,Authorization,X-Api-Key,X-Amz-Security-Token'"
    "method.response.header.Access-Control-Allow-Methods"      = "'GET,OPTIONS'"
    "method.response.header.Access-Control-Allow-Origin"       = "'*'"
    "method.response.header.Access-Control-Allow-Credentials"  = "'true'"
  }
  depends_on = [
    aws_api_gateway_integration.trail_groups_options_integration,
    aws_api_gateway_method_response.trail_groups_options_response
  ]
}

# GET /trail_groups
resource "aws_api_gateway_method" "trail_groups_get" {
  rest_api_id   = aws_api_gateway_rest_api.api.id
  resource_id   = aws_api_gateway_resource.trail_groups.id
  http_method   = "GET"
  authorization = var.authorization_type
  authorizer_id = aws_api_gateway_authorizer.cognito_authorizer.id
}

resource "aws_api_gateway_integration" "trail_groups_get_integration" {
  rest_api_id             = aws_api_gateway_rest_api.api.id
  resource_id             = aws_api_gateway_resource.trail_groups.id
  http_method             = aws_api_gateway_method.trail_groups_get.http_method
  integration_http_method = "POST"
  type                    = "AWS_PROXY"
  uri                     = aws_lambda_function.get_trail_groups.invoke_arn
}

# /csv Resource
resource "aws_api_gateway_resource" "csv" {
  path_part   = "csv"
  parent_id   = aws_api_gateway_rest_api.api.root_resource_id
  rest_api_id = aws_api_gateway_rest_api.api.id
}

# CORS (OPTIONS) for /csv
resource "aws_api_gateway_method" "csv_options" {
  rest_api_id   = aws_api_gateway_rest_api.api.id
  resource_id   = aws_api_gateway_resource.csv.id
  http_method   = "OPTIONS"
  authorization = "NONE"
}

resource "aws_api_gateway_integration" "csv_options_integration" {
  rest_api_id = aws_api_gateway_rest_api.api.id
  resource_id = aws_api_gateway_resource.csv.id
  http_method = aws_api_gateway_method.csv_options.http_method
  type        = "MOCK"
  request_templates = {
    "application/json" = "{\"statusCode\": 200}"
  }
}

resource "aws_api_gateway_method_response" "csv_options_response" {
  rest_api_id = aws_api_gateway_rest_api.api.id
  resource_id = aws_api_gateway_resource.csv.id
  http_method = aws_api_gateway_method.csv_options.http_method
  status_code = "200"
  response_parameters = {
    "method.response.header.Access-Control-Allow-Headers"      = true
    "method.response.header.Access-Control-Allow-Methods"      = true
    "method.response.header.Access-Control-Allow-Origin"       = true
    "method.response.header.Access-Control-Allow-Credentials"  = true
  }
}

resource "aws_api_gateway_integration_response" "csv_options_integration_response" {
  rest_api_id = aws_api_gateway_rest_api.api.id
  resource_id = aws_api_gateway_resource.csv.id
  http_method = aws_api_gateway_method.csv_options.http_method
  status_code = "200"
  response_parameters = {
    "method.response.header.Access-Control-Allow-Headers"      = "'Content-Type,X-Amz-Date,Authorization,X-Api-Key,X-Amz-Security-Token'"
    "method.response.header.Access-Control-Allow-Methods"      = "'GET,OPTIONS'"
    "method.response.header.Access-Control-Allow-Origin"       = "'*'"
    "method.response.header.Access-Control-Allow-Credentials"  = "'true'"
  }
  depends_on = [
    aws_api_gateway_integration.csv_options_integration,
    aws_api_gateway_method_response.csv_options_response
  ]
}

# GET /csv
resource "aws_api_gateway_method" "csv_get" {
  rest_api_id   = aws_api_gateway_rest_api.api.id
  resource_id   = aws_api_gateway_resource.csv.id
  http_method   = "GET"
  authorization = var.authorization_type
  authorizer_id = aws_api_gateway_authorizer.cognito_authorizer.id
}

resource "aws_api_gateway_integration" "csv_get_integration" {
  rest_api_id             = aws_api_gateway_rest_api.api.id
  resource_id             = aws_api_gateway_resource.csv.id
  http_method             = aws_api_gateway_method.csv_get.http_method
  integration_http_method = "POST"
  type                    = "AWS_PROXY"
  uri                     = aws_lambda_function.export_csv.invoke_arn
}

# Cognito Authorizer
resource "aws_api_gateway_authorizer" "cognito_authorizer" {
  name          = "${var.deploy_env}_CognitoAuthorizer"
  rest_api_id   = aws_api_gateway_rest_api.api.id
  type          = var.authorization_type
  provider_arns = [aws_cognito_user_pool.user_pool.arn]
}

# Deployment + Stage
resource "aws_api_gateway_deployment" "api_deployment" {
  rest_api_id = aws_api_gateway_rest_api.api.id

  triggers = {
    redeployment = sha1(jsonencode([
      aws_api_gateway_integration.trail_data_post_integration.uri,
      aws_api_gateway_integration.trail_data_get_integration.uri,
      aws_api_gateway_integration.devices_post_integration.uri,
      aws_api_gateway_integration.trail_metadata_get_integration.uri,
      aws_api_gateway_integration.trail_metadata_post_integration.uri,
      aws_api_gateway_integration.trail_metadata_put_integration.uri,
      aws_api_gateway_integration.trail_metadata_delete_integration.uri,
      aws_api_gateway_integration.device_metadata_get_integration.uri,
      aws_api_gateway_integration.device_metadata_put_integration.uri,
      aws_api_gateway_integration.trail_groups_get_integration.uri,
      aws_api_gateway_integration.csv_get_integration.uri
    ]))
  }

  lifecycle {
    create_before_destroy = true
  }

  depends_on = [
    aws_api_gateway_integration.trail_data_post_integration,
    aws_api_gateway_integration.trail_data_get_integration,
    aws_api_gateway_integration.devices_post_integration,
    aws_api_gateway_integration.trail_metadata_get_integration,
    aws_api_gateway_integration.trail_metadata_post_integration,
    aws_api_gateway_integration.trail_metadata_put_integration,
    aws_api_gateway_integration.trail_metadata_delete_integration,
    aws_api_gateway_integration.device_metadata_get_integration,
    aws_api_gateway_integration.device_metadata_put_integration,
    aws_api_gateway_integration.trail_groups_get_integration,
    aws_api_gateway_integration.csv_get_integration,
    aws_api_gateway_integration_response.trail_data_options_integration_response,
    aws_api_gateway_integration_response.devices_options_integration_response,
    aws_api_gateway_integration_response.trail_metadata_options_integration_response,
    aws_api_gateway_integration_response.device_metadata_options_integration_response,
    aws_api_gateway_integration_response.trail_groups_options_integration_response,
    aws_api_gateway_integration_response.csv_options_integration_response
  ]
}

resource "aws_api_gateway_stage" "api_stage" {
  deployment_id = aws_api_gateway_deployment.api_deployment.id
  rest_api_id   = aws_api_gateway_rest_api.api.id
  stage_name    = "${var.deploy_env}_${var.default_name}_api_stage"
}

# Environment file for frontend (.env)
resource "local_sensitive_file" "frontend_env" {
  count = var.local_run ? 1 : 0
  content = <<EOF
VITE_API_URL=${aws_api_gateway_stage.api_stage.invoke_url}
VITE_COGNITO_REGION=us-east-1
VITE_COGNITO_USER_POOL_ID=${aws_cognito_user_pool.user_pool.id}
VITE_COGNITO_CLIENT_ID=${aws_cognito_user_pool_client.client.id}
EOF
  filename = "${path.module}/${local.react_app_directory}/.env"
  depends_on = [
    aws_api_gateway_stage.api_stage,
    aws_cognito_user_pool.user_pool,
    aws_cognito_user_pool_client.client
  ]
}

resource "null_resource" "generate_id_token" {
  count = var.local_run ? 1 : 0
  provisioner "local-exec" {
    command = "aws cognito-idp initiate-auth --region us-east-1 --auth-flow USER_PASSWORD_AUTH --client-id ${aws_cognito_user_pool_client.client.id} --auth-parameters USERNAME=${var.admin_username},PASSWORD=${var.admin_password} --output json > token.json"
  }

  depends_on = [aws_cognito_user_pool_client.client, aws_cognito_user.admin]
}

data "local_file" "cognito_token_json" {
  count = var.local_run ? 1 : 0
  filename   = "${path.module}/token.json"
  depends_on = [null_resource.generate_id_token]
}

locals {
  cognito_token = var.local_run ? jsondecode(data.local_file.cognito_token_json[0].content).AuthenticationResult.IdToken : ""
}

# Environment file for testing (.env)
resource "local_sensitive_file" "testing_env" {
  count = var.local_run ? 1 : 0
  content = <<EOF
CLOUDFRONT_URL=http://${aws_cloudfront_distribution.s3_distribution[0].domain_name}
API_URL=${aws_api_gateway_stage.api_stage.invoke_url}
API_TOKEN=${local.cognito_token}
API_KEY=${aws_api_gateway_api_key.api_key.value}
EOF
  filename = "${path.module}/${local.test_directory}/.env"
  depends_on = [
    aws_api_gateway_stage.api_stage,
    aws_cognito_user_pool.user_pool,
    aws_cognito_user_pool_client.client,
    data.local_file.cognito_token_json,
    aws_cloudfront_distribution.s3_distribution
  ]
}  

# API Key 
resource "aws_api_gateway_api_key" "api_key" {
  name = "${var.deploy_env} Device API Key"
  value = "${var.deploy_env}-trail-planner-key-trail-trail-trail-trail"
}

# API Gateway Usage Plan
resource "aws_api_gateway_usage_plan" "device_usage_plan" {
  name = "${var.deploy_env} Device API Usage Plan"

  api_stages {
    api_id = aws_api_gateway_rest_api.api.id
    stage  = aws_api_gateway_stage.api_stage.stage_name
  }

  throttle_settings {
    burst_limit = 100
    rate_limit  = 50
  }

  quota_settings {
    limit  = 10000
    period = "DAY"
  }

  depends_on = [aws_api_gateway_stage.api_stage]
}

# Associate API Key with Usage Plan
resource "aws_api_gateway_usage_plan_key" "device_usage_plan_key" {
  key_id        = aws_api_gateway_api_key.api_key.id
  key_type      = "API_KEY"
  usage_plan_id = aws_api_gateway_usage_plan.device_usage_plan.id

  depends_on = [
    aws_api_gateway_api_key.api_key,
    aws_api_gateway_usage_plan.device_usage_plan
  ]
}

# Output
output "api_gateway_url" {
  value = aws_api_gateway_stage.api_stage.invoke_url
}