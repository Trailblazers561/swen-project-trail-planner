locals {
  device_registration_api_endpoints = {
    register_device = {
      POST = {
        file = "register_device/register_device_post.py"
        handler = "register_device_post.register_device"
      }
    }
  }

  device_registration_api_methods = merge([
    for endpoint, methods in local.device_registration_api_endpoints : {
      for method, config in methods :
      "${endpoint}_${lower(method)}" => merge(
        { endpoint = endpoint, method = method,  },
        config
      )
    }
  ]...)
  device_registration_api_methods_per_endpoint = {
    for endpoint, methods in local.device_registration_api_endpoints :
    endpoint => [
      for method, _ in methods : method
    ]
  }
}

# API Gateway (REST API)
resource "aws_api_gateway_rest_api" "device_registration_api" {
  body = jsonencode({
    openapi = "3.0.1"
    info = {
      title   = "${var.deploy_env}_trailcount_device_registration_api"
      version = "1.0"
    }
  })
  name = "${var.deploy_env}_trailcount_device_registration_api"
}

resource "aws_api_gateway_domain_name" "device_registration_api_domain" {
  count = local.use_domain ? 1 : 0
  domain_name = "${local.registration_api_sub_domain}.${local.domain}"
  regional_certificate_arn = var.acm_certificate_arn

  endpoint_configuration {
    types = ["REGIONAL"]
  }

  security_policy = "SecurityPolicy_TLS13_1_2_2021_06"
  endpoint_access_mode = "STRICT"
}

resource "aws_api_gateway_base_path_mapping" "registration_api_mapping" {
  count = local.use_domain ? 1 : 0
  api_id      = aws_api_gateway_rest_api.device_registration_api.id
  stage_name  = aws_api_gateway_stage.device_registration_api_stage.stage_name
  domain_name = aws_api_gateway_domain_name.device_registration_api_domain[0].domain_name
}

resource "aws_api_gateway_stage" "device_registration_api_stage" {
  deployment_id = aws_api_gateway_deployment.device_registration_api_deployment.id
  rest_api_id   = aws_api_gateway_rest_api.device_registration_api.id
  stage_name    = "${var.deploy_env}_trailcount_device_registration_api_stage"
}

# API Gateway Usage Plan
resource "aws_api_gateway_usage_plan" "device_registration_api_usage_plan" {
  name = "${var.deploy_env} TrailCount Device Registration API Usage Plan"

  api_stages {
    api_id = aws_api_gateway_rest_api.device_registration_api.id
    stage  = aws_api_gateway_stage.device_registration_api_stage.stage_name
  }

  throttle_settings {
    burst_limit = 100
    rate_limit  = 50
  }

  quota_settings {
    limit  = 10000
    period = "DAY"
  }

  depends_on = [aws_api_gateway_stage.device_registration_api_stage]
}

# Output
output "device_registration_api_gateway_url" {
  value = aws_api_gateway_stage.device_registration_api_stage.invoke_url
}

// Create Each Device Registration API Lambda Zip File
data "archive_file" "device_registration_api_lambda_zips" {
  for_each = local.device_registration_api_methods

  type = "zip"
  source_file = "${path.module}/${local.lambda_code_directory}/registration_api/${each.value.file}"
  output_path = "${path.module}/${local.lambda_code_directory}/zips/${each.key}.zip"
}

// Create Each Device Registration API Lambda
resource "aws_lambda_function" "device_registration_api_lambdas" {
  for_each = local.device_registration_api_methods

  function_name = "${var.deploy_env}_trailcount_${each.key}"
  role = aws_iam_role.lambda_iam_role.arn
  handler = "${each.value.handler}"
  runtime = "python3.12"
  filename = data.archive_file.device_registration_api_lambda_zips[each.key].output_path
  source_code_hash = data.archive_file.device_registration_api_lambda_zips[each.key].output_base64sha256
  timeout = lookup(each.value, "timeout", 3)
  layers = [aws_lambda_layer_version.helper_layer.arn]

  environment {
    variables = {
      REGISTRATION_TABLE = aws_dynamodb_table.registration_table.name
      DEVICE_TRAIL_LOG_HOUR_TABLE = aws_dynamodb_table.device_trail_log_hour_table.name
      DEVICE_TRAIL_LOG_DAY_TABLE = aws_dynamodb_table.device_trail_log_day_table.name
      DEVICE_TRAIL_LOG_WEEK_TABLE = aws_dynamodb_table.device_trail_log_week_table.name
      DEVICE_TRAIL_LOG_MONTH_TABLE = aws_dynamodb_table.device_trail_log_month_table.name
      TRAIL_TABLE = aws_dynamodb_table.trail_table.name
      DEVICE_TABLE = aws_dynamodb_table.device_table.name
      DEVICE_TRAIL_TABLE = aws_dynamodb_table.device_trail_table.name
      AREA_TABLE = aws_dynamodb_table.area_table.name
      TRAIL_CSV_BUCKET = aws_s3_bucket.csv_bucket.bucket
      COGNITO_USER_POOL_ID = aws_cognito_user_pool.user_pool.id
      DEVICE_LOG_TABLE = aws_dynamodb_table.device_log_table.name
      DEPLOY_ENV = var.deploy_env
    }
  }
}

// Allow Lambdas To Be Invoked By An API
resource "aws_lambda_permission" "allow_apigateway_device_registration_api_lambdas" {
  for_each = aws_lambda_function.device_registration_api_lambdas

  statement_id  = "AllowAPIGatewayInvoke-${each.key}"
  action        = "lambda:InvokeFunction"
  function_name = each.value.function_name
  principal     = "apigateway.amazonaws.com"

  source_arn = "${aws_api_gateway_rest_api.device_registration_api.execution_arn}/*/*"
}

// Create API Endpoints
resource "aws_api_gateway_resource" "device_registration_api_resources" {
  for_each = local.device_registration_api_endpoints

  path_part = each.key
  parent_id = aws_api_gateway_rest_api.device_registration_api.root_resource_id
  rest_api_id = aws_api_gateway_rest_api.device_registration_api.id
}

// Create API Methods
resource "aws_api_gateway_method" "device_registration_api_methods" {
  for_each = local.device_registration_api_methods

  rest_api_id = aws_api_gateway_rest_api.device_registration_api.id
  resource_id = aws_api_gateway_resource.device_registration_api_resources[each.value.endpoint].id
  http_method   = each.value.method
  authorization = "NONE"
}

resource "aws_api_gateway_integration" "device_registration_api_integrations" {
  for_each = local.device_registration_api_methods

  rest_api_id = aws_api_gateway_rest_api.device_registration_api.id
  resource_id = aws_api_gateway_resource.device_registration_api_resources[each.value.endpoint].id
  http_method = aws_api_gateway_method.device_registration_api_methods[each.key].http_method

  integration_http_method = "POST"
  type                    = "AWS_PROXY"

  uri = aws_lambda_function.device_registration_api_lambdas[each.key].invoke_arn
}

// Setup OPTIONS methods for each endpoint
resource "aws_api_gateway_method" "device_registration_api_options_methods" {
  for_each = local.device_registration_api_endpoints

  rest_api_id = aws_api_gateway_rest_api.device_registration_api.id
  resource_id = aws_api_gateway_resource.device_registration_api_resources[each.key].id
  http_method = "OPTIONS"
  authorization = "NONE"
}

resource "aws_api_gateway_integration" "device_registration_api_options_integrations" {
  for_each = local.device_registration_api_endpoints

  rest_api_id = aws_api_gateway_rest_api.device_registration_api.id
  resource_id = aws_api_gateway_resource.device_registration_api_resources[each.key].id
  http_method = aws_api_gateway_method.device_registration_api_options_methods[each.key].http_method
  type = "MOCK"

  request_templates = {
    "application/json" = "{\"statusCode\": 200}"
  }
}

resource "aws_api_gateway_method_response" "device_registration_api_options_method_responses" {
  for_each = local.device_registration_api_endpoints

  rest_api_id = aws_api_gateway_rest_api.device_registration_api.id
  resource_id = aws_api_gateway_resource.device_registration_api_resources[each.key].id
  http_method = aws_api_gateway_method.device_registration_api_options_methods[each.key].http_method
  status_code = "200"

  response_parameters = {
    "method.response.header.Access-Control-Allow-Headers" = true
    "method.response.header.Access-Control-Allow-Methods" = true
    "method.response.header.Access-Control-Allow-Origin" = true
    "method.response.header.Access-Control-Allow-Credentials" = true
  }
}

resource "aws_api_gateway_integration_response" "device_registration_api_options_integration_responses" {
  for_each = local.device_registration_api_endpoints

  rest_api_id = aws_api_gateway_rest_api.device_registration_api.id
  resource_id = aws_api_gateway_resource.device_registration_api_resources[each.key].id
  http_method = aws_api_gateway_method.device_registration_api_options_methods[each.key].http_method
  status_code = "200"

  response_parameters = {
    "method.response.header.Access-Control-Allow-Headers"      = "'Content-Type,X-Amz-Date,Authorization,X-Api-Key,X-Amz-Security-Token'"
    "method.response.header.Access-Control-Allow-Methods"      = "'${join(",", concat(local.device_registration_api_methods_per_endpoint[each.key], ["OPTIONS"]))}'"
    "method.response.header.Access-Control-Allow-Origin"       = "'*'"
    "method.response.header.Access-Control-Allow-Credentials"  = "'true'"
  }

  depends_on = [
    aws_api_gateway_integration.device_registration_api_options_integrations,
    aws_api_gateway_method_response.device_registration_api_options_method_responses
  ]
}

# Deployment + Stage
resource "aws_api_gateway_deployment" "device_registration_api_deployment" {
  rest_api_id = aws_api_gateway_rest_api.device_registration_api.id

  triggers = {
    redeployment = sha1(jsonencode(concat(
      # Regular Methods
      [ for m in aws_api_gateway_method.device_registration_api_methods : m.authorization ],
      # Regular Integrations
      [ for i in aws_api_gateway_integration.device_registration_api_integrations : i.uri ],
      # Options Methods
      [ for m in aws_api_gateway_method.device_registration_api_options_methods : m.authorization ],
      # Options Integrations
      [ for i in aws_api_gateway_integration.device_registration_api_options_integrations : i.uri ],
      # Options Integration Responses
      [ for r in aws_api_gateway_integration_response.device_registration_api_options_integration_responses : r.response_parameters ],
    )))
  }

  lifecycle {
    create_before_destroy = true
  }

  depends_on = [
    aws_api_gateway_integration.device_registration_api_integrations,
    aws_api_gateway_integration.device_registration_api_options_integrations,
    aws_api_gateway_integration_response.device_registration_api_options_integration_responses
  ]
}