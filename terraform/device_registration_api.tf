# API Gateway (REST API)
resource "aws_api_gateway_rest_api" "registration_api" {
  body = jsonencode({
    openapi = "3.0.1"
    info = {
      title   = "${var.deploy_env}_trailplanner_registration_api"
      version = "1.0"
    }
  })
  name = "${var.deploy_env}_trailplanner_registration_api"
}

# /register_device Resource
resource "aws_api_gateway_resource" "register_device" {
  path_part   = "register_device"
  parent_id   = aws_api_gateway_rest_api.registration_api.root_resource_id
  rest_api_id = aws_api_gateway_rest_api.registration_api.id
}

# POST /register_device -> Lambda register_device:
resource "aws_api_gateway_method" "register_device_post" {
  rest_api_id   = aws_api_gateway_rest_api.registration_api.id
  resource_id   = aws_api_gateway_resource.register_device.id
  http_method   = "POST"
  authorization = "NONE"
}

resource "aws_api_gateway_integration" "register_device_post_integration" {
  rest_api_id             = aws_api_gateway_rest_api.registration_api.id
  resource_id             = aws_api_gateway_resource.register_device.id
  http_method             = aws_api_gateway_method.register_device_post.http_method
  integration_http_method = "POST"
  type                    = "AWS_PROXY"
  uri                     = aws_lambda_function.device_cert_registration.invoke_arn
}

# Deployment + Stage
resource "aws_api_gateway_deployment" "registration_api_deployment" {
  rest_api_id = aws_api_gateway_rest_api.registration_api.id

  triggers = {
    redeployment = sha1(jsonencode([
      # Integrations
      aws_api_gateway_integration.register_device_post_integration.uri,

      # Methods
      aws_api_gateway_method.register_device_post.authorization,

      # Permissions
      aws_lambda_permission.allow_registration_api_register_device.id
    ]))
  }

  lifecycle {
    create_before_destroy = true
  }

  depends_on = [
    aws_api_gateway_integration.register_device_post_integration,
  ]
}

resource "aws_api_gateway_stage" "registration_api_stage" {
  deployment_id = aws_api_gateway_deployment.registration_api_deployment.id
  rest_api_id   = aws_api_gateway_rest_api.registration_api.id
  stage_name    = "${var.deploy_env}_trailplanner_registration_api_stage"
}

resource "aws_lambda_permission" "allow_registration_api_register_device" {
  statement_id = "AllowRegistrationAPIInvokeRegisterDevice"
  action = "lambda:InvokeFunction"
  function_name = aws_lambda_function.device_cert_registration.function_name
  principal = "apigateway.amazonaws.com"
  source_arn = "${aws_api_gateway_rest_api.registration_api.execution_arn}/*/*"
}