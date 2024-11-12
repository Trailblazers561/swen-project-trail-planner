resource "aws_api_gateway_rest_api" "api" {
  body = jsonencode({
    openapi = "3.0.1"
    info = {
      title   = "${var.default_name}_api"
      version = "1.0"
    }
  })
  name = "${var.default_name}_api"
}

resource "aws_api_gateway_resource" "trail_data" {
  path_part   = "trail_data"
  parent_id   = aws_api_gateway_rest_api.api.root_resource_id
  rest_api_id = aws_api_gateway_rest_api.api.id
}

#Fixes CORS issues by setting up preflight
resource "aws_api_gateway_method" "trail_data_options" {
  rest_api_id   = aws_api_gateway_rest_api.api.id
  resource_id   = aws_api_gateway_resource.trail_data.id
  http_method   = "OPTIONS"
  authorization = "NONE"

  depends_on = [aws_api_gateway_resource.trail_data ]
}

resource "aws_api_gateway_model" "trail_data_response_model" {
  rest_api_id = aws_api_gateway_rest_api.api.id
  content_type = "application/json"
  name = "TrailDataResponseModel"

  schema = <<EOF
  {
    "type": "object",
    "properties": {
      "statusCode": { "type": "integer" }
    }
  }
  EOF
}

resource "aws_api_gateway_method_response" "trail_data_options_response" {
  rest_api_id = aws_api_gateway_rest_api.api.id
  resource_id = aws_api_gateway_resource.trail_data.id
  http_method = aws_api_gateway_method.trail_data_options.http_method
  status_code = 200 

  response_models = {
    "application/json" = aws_api_gateway_model.trail_data_response_model.name
  }

  response_parameters = {
    "method.response.header.Access-Control-Allow-Credentials" = true,
    "method.response.header.Access-Control-Allow-Headers" = true
    "method.response.header.Access-Control-Allow-Methods" = true,
    "method.response.header.Access-Control-Allow-Origin"  = true,
  }

  depends_on = [aws_api_gateway_method.trail_data_options, aws_api_gateway_model.trail_data_response_model]
}

resource "aws_api_gateway_integration" "trail_data_options_integration" {
  rest_api_id             = aws_api_gateway_rest_api.api.id
  resource_id             = aws_api_gateway_resource.trail_data.id
  http_method             = aws_api_gateway_method.trail_data_options.http_method

  type                    = "MOCK"

  request_templates = {
    "application/json" = "{ \"statusCode\": 200 }"
  }

  depends_on = [aws_api_gateway_method.trail_data_options]
}

resource "aws_api_gateway_integration_response" "trail_data_options_integration_response" {
  rest_api_id = aws_api_gateway_rest_api.api.id
  resource_id = aws_api_gateway_resource.trail_data.id
  http_method = aws_api_gateway_method.trail_data_options.http_method
  status_code = aws_api_gateway_method_response.trail_data_options_response.status_code

  response_parameters = {
    "method.response.header.Access-Control-Allow-Credentials" = "'true'"
    "method.response.header.Access-Control-Allow-Origin"  = "'*'",
    "method.response.header.Access-Control-Allow-Headers" = "'Content-Type,X-Amz-Date,Authorization,X-Api-Key,X-Amz-Security-Token'" 
    "method.response.header.Access-Control-Allow-Methods" = "'OPTIONS,POST'",
  }

  depends_on = [aws_api_gateway_method_response.trail_data_options_response]
}

resource "aws_api_gateway_method" "trail_data_post" {
  rest_api_id   = aws_api_gateway_rest_api.api.id
  resource_id   = aws_api_gateway_resource.trail_data.id
  http_method   = "POST"
  authorization = var.authorization_type
  authorizer_id = aws_api_gateway_authorizer.cognito_authorizer.id

  depends_on = [aws_api_gateway_resource.trail_data]
}

resource "aws_api_gateway_method_response" "trail_data_method_response" {
  rest_api_id = aws_api_gateway_rest_api.api.id
  resource_id = aws_api_gateway_resource.trail_data.id
  http_method = aws_api_gateway_method.trail_data_post.http_method
  status_code = 200 

  response_parameters = {
    "method.response.header.Access-Control-Allow-Origin" = true,
  }

  depends_on = [aws_api_gateway_method.trail_data_post]
}

resource "aws_api_gateway_integration" "trail_data_integration" {
  rest_api_id             = aws_api_gateway_rest_api.api.id
  resource_id             = aws_api_gateway_resource.trail_data.id
  http_method             = aws_api_gateway_method.trail_data_post.http_method
  integration_http_method = "POST"
  type                    = "AWS_PROXY"
  uri                     = aws_lambda_function.upload_trail_data.invoke_arn

  depends_on = [ aws_api_gateway_method.trail_data_post]
}

resource "aws_api_gateway_method" "trail_data_get" {
  rest_api_id   = aws_api_gateway_rest_api.api.id
  resource_id   = aws_api_gateway_resource.trail_data.id
  http_method   = "GET"
  authorization = var.authorization_type
  authorizer_id = aws_api_gateway_authorizer.cognito_authorizer.id

  depends_on = [aws_api_gateway_resource.trail_data]
}

resource "aws_api_gateway_method_response" "trail_data_get_method_response" {
  rest_api_id = aws_api_gateway_rest_api.api.id
  resource_id = aws_api_gateway_resource.trail_data.id
  http_method = aws_api_gateway_method.trail_data_get.http_method
  status_code = 200 

  response_parameters = {
    "method.response.header.Access-Control-Allow-Origin" = true,
  }

  depends_on = [aws_api_gateway_method.trail_data_get]
}

resource "aws_api_gateway_integration" "trail_data_get_integration" {
  rest_api_id             = aws_api_gateway_rest_api.api.id
  resource_id             = aws_api_gateway_resource.trail_data.id
  http_method             = aws_api_gateway_method.trail_data_get.http_method
  integration_http_method = "POST"
  type                    = "AWS_PROXY"
  uri                     = aws_lambda_function.get_trail_data.invoke_arn

  depends_on = [ aws_api_gateway_method.trail_data_get]
}

resource "aws_api_gateway_authorizer" "cognito_authorizer" {
  name          = "CognitoAuthorizer"
  rest_api_id   = aws_api_gateway_rest_api.api.id
  type          = var.authorization_type
  provider_arns = [aws_cognito_user_pool.user_pool.arn]
}

resource "aws_api_gateway_deployment" "api_deployment" {
  rest_api_id = aws_api_gateway_rest_api.api.id

  triggers = {
    redeployment = jsonencode(aws_api_gateway_rest_api.api.body)
  }

  lifecycle {
    create_before_destroy = true
  }

  depends_on = [ aws_api_gateway_integration.trail_data_integration, aws_api_gateway_integration.trail_data_get_integration,  aws_api_gateway_integration_response.trail_data_options_integration_response]
}

resource "aws_api_gateway_stage" "api_stage" {
    deployment_id = aws_api_gateway_deployment.api_deployment.id
    rest_api_id   = aws_api_gateway_rest_api.api.id
    
    stage_name    = "${var.default_name}_api_stage"
}

output "api_gateway_url" {
    value = aws_api_gateway_stage.api_stage.invoke_url
}