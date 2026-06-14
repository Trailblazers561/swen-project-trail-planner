locals {
  public_api_endpoints = {
    areas = {
      GET = {
        file = "areas/areas_get.py"
        handler = "areas_get.get_areas"
      }
      POST = {
        file = "areas/areas_post.py"
        handler = "areas_post.create_area"
      }
      PUT = {
        file = "areas/areas_put.py"
        handler = "areas_put.update_area"
      }
      DELETE = {
        file = "areas/areas_delete.py"
        handler = "areas_delete.retire_area"
      }
    }
    csv = {
      GET = {
        file = "csv/csv_get.py"
        handler = "csv_get.create_and_fill_csv"
        timeout = 30
      }
      POST = {
        file = "csv/csv_post.py"
        handler = "csv_post.parse_csv_and_export_data"
        timeout = 600
      }
    }
    csv_url = {
      GET = {
        file = "csv_url/csv_url_get.py"
        handler = "csv_url_get.generate_url"
      }
    }
    device_metadata = {
      GET = {
        file = "device_metadata/device_metadata_get.py"
        handler = "device_metadata_get.get_device_metadata"
      }
      PUT = {
        file = "device_metadata/device_metadata_put.py"
        handler = "device_metadata_put.update_device_trail_association"
      }
    }
    devices = {
      POST = {
        file = "devices/devices_post.py"
        handler = "devices_post.upload_device_info"
      }
      PUT = {
        file = "devices/devices_put.py"
        handler = "devices_put.upload_device_data"
      }
    }
    device_management = {
      GET = {
        file = "device_management/device_management_get.py"
        handler = "device_management_get.get_device_management"
      }
    }
    block = {
      PUT = {
        file = "block/block_put.py"
        handler = "block_put.set_device_blocked"
      }
    }
    archive = {
      PUT = {
        file = "archive/archive_put.py"
        handler = "archive_put.set_device_archived"
      }
    }
    heatmap = {
      GET = {
        file = "heatmap/heatmap_get.py"
        handler = "heatmap_get.get_heatmap_data"
        timeout = 10
      }
    }
    registration = {
      GET = {
        file = "registration/registration_get.py"
        handler = "registration_get.get_registrations"
        timeout = 10
      }
      POST = {
        file = "registration/registration_post.py"
        handler = "registration_post.pre_register_device"
      }
      PUT = {
        file = "registration/registration_put.py"
        handler = "registration_put.edit_registration"
      }
      DELETE = {
        file = "registration/registration_delete.py"
        handler = "registration_delete.delete_registration"
      }
    }
    trail_data = {
      GET = {
        file = "trail_data/trail_data_get.py"
        handler = "trail_data_get.get_trail_data"
        timeout = 10
      }
      POST = {
        file = "trail_data/trail_data_post.py"
        handler = "trail_data_post.upload_trail_data"
      }
    }
    trail_metadata = {
      GET = {
        file = "trail_metadata/trail_metadata_get.py"
        handler = "trail_metadata_get.get_trail_metadata"
      }
      POST = {
        file = "trail_metadata/trail_metadata_post.py"
        handler = "trail_metadata_post.create_trail"
      }
      PUT = {
        file = "trail_metadata/trail_metadata_put.py"
        handler = "trail_metadata_put.update_trail_metadata"
      }
      DELETE = {
        file = "trail_metadata/trail_metadata_delete.py"
        handler = "trail_metadata_delete.retire_trail"
      }
    }
    users = {
      GET = {
        file = "users/users_get.py"
        handler = "users_get.get_users"
        timeout = 10
      }
      PUT = {
        file = "users/users_put.py"
        handler = "users_put.change_user_group"
      }
      DELETE = {
        file = "users/users_delete.py"
        handler = "users_delete.ban_user"
      }
    }
  }

  public_api_methods = merge([
    for endpoint, methods in local.public_api_endpoints : {
      for method, config in methods :
      "${endpoint}_${lower(method)}" => merge(
        { endpoint = endpoint, method = method,  },
        config
      )
    }
  ]...)
  public_api_methods_per_endpoint = {
    for endpoint, methods in local.public_api_endpoints :
    endpoint => [
      for method, _ in methods : method
    ]
  }
}

# API Gateway (REST API)
resource "aws_api_gateway_rest_api" "public_api" {
  body = jsonencode({
    openapi = "3.0.1"
    info = {
      title   = "${var.deploy_env}_trailcount_public_api"
      version = "1.0"
    }
  })
  name = "${var.deploy_env}_trailcount_public_api"
}

resource "aws_api_gateway_domain_name" "api_domain" {
  count = local.use_domain ? 1 : 0
  domain_name = "${local.api_sub_domain}.${local.domain}"
  regional_certificate_arn = var.acm_certificate_arn

  endpoint_configuration {
    types = ["REGIONAL"]
  }

  security_policy = "SecurityPolicy_TLS13_1_2_2021_06"
  endpoint_access_mode = "STRICT"
}

resource "aws_api_gateway_base_path_mapping" "api_mapping" {
  count = local.use_domain ? 1 : 0
  api_id      = aws_api_gateway_rest_api.public_api.id
  stage_name  = aws_api_gateway_stage.api_stage.stage_name
  domain_name = aws_api_gateway_domain_name.api_domain[0].domain_name
}

resource "aws_api_gateway_stage" "api_stage" {
  deployment_id = aws_api_gateway_deployment.public_api_deployment.id
  rest_api_id   = aws_api_gateway_rest_api.public_api.id
  stage_name    = "${var.deploy_env}_trailcount_public_api_stage"
}

# API Key 
resource "aws_api_gateway_api_key" "api_key" {
  name = "${var.deploy_env} TrailCount Device API Key"
  value = "${var.deploy_env}-trail-count-key-trail-trail-trail-trail"
}

# API Gateway Usage Plan
resource "aws_api_gateway_usage_plan" "public_api_usage_plan" {
  name = "${var.deploy_env} TrailCount Public API Usage Plan"

  api_stages {
    api_id = aws_api_gateway_rest_api.public_api.id
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

# Associate API Key with Usage Plan (Will Get Removed With MTLS)
resource "aws_api_gateway_usage_plan_key" "device_usage_plan_key" {
  key_id        = aws_api_gateway_api_key.api_key.id
  key_type      = "API_KEY"
  usage_plan_id = aws_api_gateway_usage_plan.public_api_usage_plan.id

  depends_on = [
    aws_api_gateway_api_key.api_key,
    aws_api_gateway_usage_plan.public_api_usage_plan
  ]
}

# Output
output "api_gateway_url" {
  value = aws_api_gateway_stage.api_stage.invoke_url
}

# Create Helper Function Layer 
resource "null_resource" "helper_layer_setup" {
  count = local.local_run ? 1 : 0

  triggers = {
    shell_hash = filesha256("${path.module}/${local.lambda_code_directory}/helper_functions.py")
  }

  provisioner "local-exec" {
    command = "(if not exist ${path.module}\\..\\lambdas\\layers\\helper\\python mkdir ${path.module}\\..\\lambdas\\layers\\helper\\python) && copy /Y ${path.module}\\..\\lambdas\\helper_functions.py ${path.module}\\..\\lambdas\\layers\\helper\\python\\helper_functions.py"
  }
}

data "archive_file" "helper_layer" {
  type = "zip"
  source_dir = "${path.module}/${local.lambda_code_directory}/layers/helper"
  output_path = "${path.module}/${local.lambda_code_directory}/zips/helper_layer.zip"
  depends_on = [null_resource.helper_layer_setup]
}

resource "aws_lambda_layer_version" "helper_layer" {
  layer_name = "${var.deploy_env}-trailcount-helper-layer"
  filename = data.archive_file.helper_layer.output_path
  source_code_hash = data.archive_file.helper_layer.output_base64sha256
  compatible_runtimes = ["python3.12"]
}

// Create Each Public API Lambda Zip File
data "archive_file" "public_api_lambda_zips" {
  for_each = local.public_api_methods

  type = "zip"
  source_file = "${path.module}/${local.lambda_code_directory}/public_api/${each.value.file}"
  output_path = "${path.module}/${local.lambda_code_directory}/zips/${each.key}.zip"
}

// Create Each Public API Lambda
resource "aws_lambda_function" "public_api_lambdas" {
  for_each = local.public_api_methods

  function_name = "${var.deploy_env}_trailcount_${each.key}"
  role = aws_iam_role.lambda_iam_role.arn
  handler = "${each.value.handler}"
  runtime = "python3.12"
  filename = data.archive_file.public_api_lambda_zips[each.key].output_path
  source_code_hash = data.archive_file.public_api_lambda_zips[each.key].output_base64sha256
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
    }
  }
}

// Allow Lambdas To Be Invoked By An API
resource "aws_lambda_permission" "allow_apigateway_public_api_lambdas" {
  for_each = aws_lambda_function.public_api_lambdas

  statement_id  = "AllowAPIGatewayInvoke-${each.key}"
  action        = "lambda:InvokeFunction"
  function_name = each.value.function_name
  principal     = "apigateway.amazonaws.com"

  source_arn = "${aws_api_gateway_rest_api.public_api.execution_arn}/*/*"
}

// Create API Endpoints
resource "aws_api_gateway_resource" "public_api_resources" {
  for_each = local.public_api_endpoints

  path_part = each.key
  parent_id = aws_api_gateway_rest_api.public_api.root_resource_id
  rest_api_id = aws_api_gateway_rest_api.public_api.id
}

// Create API Methods
resource "aws_api_gateway_method" "public_api_methods" {
  for_each = local.public_api_methods

  rest_api_id = aws_api_gateway_rest_api.public_api.id
  resource_id = aws_api_gateway_resource.public_api_resources[each.value.endpoint].id
  http_method   = each.value.method
  authorization = local.gateway_method_authorization
  authorizer_id = aws_api_gateway_authorizer.lambda_authorizer.id
}

resource "aws_api_gateway_integration" "public_api_integrations" {
  for_each = local.public_api_methods

  rest_api_id = aws_api_gateway_rest_api.public_api.id
  resource_id = aws_api_gateway_resource.public_api_resources[each.value.endpoint].id
  http_method = aws_api_gateway_method.public_api_methods[each.key].http_method

  integration_http_method = "POST"
  type                    = "AWS_PROXY"

  uri = aws_lambda_function.public_api_lambdas[each.key].invoke_arn
}

// Setup OPTIONS methods for each endpoint
resource "aws_api_gateway_method" "public_api_options_methods" {
  for_each = local.public_api_endpoints

  rest_api_id = aws_api_gateway_rest_api.public_api.id
  resource_id = aws_api_gateway_resource.public_api_resources[each.key].id
  http_method = "OPTIONS"
  authorization = "NONE"
}

resource "aws_api_gateway_integration" "public_api_options_integrations" {
  for_each = local.public_api_endpoints

  rest_api_id = aws_api_gateway_rest_api.public_api.id
  resource_id = aws_api_gateway_resource.public_api_resources[each.key].id
  http_method = aws_api_gateway_method.public_api_options_methods[each.key].http_method
  type = "MOCK"

  request_templates = {
    "application/json" = "{\"statusCode\": 200}"
  }
}

resource "aws_api_gateway_method_response" "public_api_options_method_responses" {
  for_each = local.public_api_endpoints

  rest_api_id = aws_api_gateway_rest_api.public_api.id
  resource_id = aws_api_gateway_resource.public_api_resources[each.key].id
  http_method = aws_api_gateway_method.public_api_options_methods[each.key].http_method
  status_code = "200"

  response_parameters = {
    "method.response.header.Access-Control-Allow-Headers" = true
    "method.response.header.Access-Control-Allow-Methods" = true
    "method.response.header.Access-Control-Allow-Origin" = true
    "method.response.header.Access-Control-Allow-Credentials" = true
  }
}

resource "aws_api_gateway_integration_response" "public_api_options_integration_responses" {
  for_each = local.public_api_endpoints

  rest_api_id = aws_api_gateway_rest_api.public_api.id
  resource_id = aws_api_gateway_resource.public_api_resources[each.key].id
  http_method = aws_api_gateway_method.public_api_options_methods[each.key].http_method
  status_code = "200"

  response_parameters = {
    "method.response.header.Access-Control-Allow-Headers"      = "'Content-Type,X-Amz-Date,Authorization,X-Api-Key,X-Amz-Security-Token'"
    "method.response.header.Access-Control-Allow-Methods"      = "'${join(",", concat(local.public_api_methods_per_endpoint[each.key], ["OPTIONS"]))}'"
    "method.response.header.Access-Control-Allow-Origin"       = "'*'"
    "method.response.header.Access-Control-Allow-Credentials"  = "'true'"
  }

  depends_on = [
    aws_api_gateway_integration.public_api_options_integrations,
    aws_api_gateway_method_response.public_api_options_method_responses
  ]
}

# Lambda Authorizer Authorizer
resource "aws_api_gateway_authorizer" "lambda_authorizer" {
  name = "${var.deploy_env}_trailcount_lambda_authorizer"
  rest_api_id = aws_api_gateway_rest_api.public_api.id
  authorizer_uri = aws_lambda_function.lambda_authorizer.invoke_arn
  type = local.gateway_authorizer_type
  authorizer_result_ttl_in_seconds =  0
}

# Deployment + Stage
resource "aws_api_gateway_deployment" "public_api_deployment" {
  rest_api_id = aws_api_gateway_rest_api.public_api.id

  triggers = {
    redeployment = sha1(jsonencode(concat(
      # Regular Methods
      [ for m in aws_api_gateway_method.public_api_methods : m.authorization ],
      # Regular Integrations
      [ for i in aws_api_gateway_integration.public_api_integrations : i.uri ],
      # Options Methods
      [ for m in aws_api_gateway_method.public_api_options_methods : m.authorization ],
      # Options Integrations
      [ for i in aws_api_gateway_integration.public_api_options_integrations : i.uri ],
      # Options Integration Responses
      [ for r in aws_api_gateway_integration_response.public_api_options_integration_responses : r.response_parameters ],
      # Authorizer Stuff / Permissions
      [
        aws_api_gateway_authorizer.lambda_authorizer.id,
        aws_api_gateway_authorizer.lambda_authorizer.authorizer_uri,
        aws_lambda_permission.allow_apigateway_public_api_lambdas
      ]
    )))
  }

  lifecycle {
    create_before_destroy = true
  }

  depends_on = [
    aws_api_gateway_integration.public_api_integrations,
    aws_api_gateway_integration.public_api_options_integrations,
    aws_api_gateway_integration_response.public_api_options_integration_responses
  ]
}