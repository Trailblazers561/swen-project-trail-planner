# API Gateway (REST API)
resource "aws_api_gateway_rest_api" "device_api" {
  body = jsonencode({
    openapi = "3.0.1"
    info = {
      title   = "${var.deploy_env}_trailplanner_device_api"
      version = "1.0"
    }
  })
  name = "${var.deploy_env}_trailplanner_device_api"
}

# /renew Resource
resource "aws_api_gateway_resource" "renew" {
  path_part   = "renew"
  parent_id   = aws_api_gateway_rest_api.device_api.root_resource_id
  rest_api_id = aws_api_gateway_rest_api.device_api.id
}

# CORS (OPTIONS) for /renew
resource "aws_api_gateway_method" "renew_options" {
  rest_api_id   = aws_api_gateway_rest_api.device_api.id
  resource_id   = aws_api_gateway_resource.renew.id
  http_method   = "OPTIONS"
  authorization = "NONE"
}

resource "aws_api_gateway_integration" "renew_options_integration" {
  rest_api_id = aws_api_gateway_rest_api.device_api.id
  resource_id = aws_api_gateway_resource.renew.id
  http_method = aws_api_gateway_method.renew_options.http_method
  type        = "MOCK"

  request_templates = {
    "application/json" = "{\"statusCode\": 200}"
  }
}

resource "aws_api_gateway_method_response" "renew_options_response" {
  rest_api_id = aws_api_gateway_rest_api.device_api.id
  resource_id = aws_api_gateway_resource.renew.id
  http_method = aws_api_gateway_method.renew_options.http_method
  status_code = "200"

  response_parameters = {
    "method.response.header.Access-Control-Allow-Headers"      = true
    "method.response.header.Access-Control-Allow-Methods"      = true
    "method.response.header.Access-Control-Allow-Origin"       = true
    "method.response.header.Access-Control-Allow-Credentials"  = true
  }
}

resource "aws_api_gateway_integration_response" "renew_options_integration_response" {
  rest_api_id = aws_api_gateway_rest_api.device_api.id
  resource_id = aws_api_gateway_resource.renew.id
  http_method = aws_api_gateway_method.renew_options.http_method
  status_code = "200"

  response_parameters = {
    "method.response.header.Access-Control-Allow-Headers"      = "'Content-Type,X-Amz-Date,Authorization,X-Api-Key,X-Amz-Security-Token'"
    "method.response.header.Access-Control-Allow-Methods"      = "'POST,OPTIONS'"
    "method.response.header.Access-Control-Allow-Origin"       = "'*'"
    "method.response.header.Access-Control-Allow-Credentials"  = "'true'"
  }

  depends_on = [
    aws_api_gateway_integration.renew_options_integration,
    aws_api_gateway_method_response.renew_options_response
  ]
}

# PUT /renew -> Lambda: renew_certificate
resource "aws_api_gateway_method" "renew_put" {
  rest_api_id   = aws_api_gateway_rest_api.device_api.id
  resource_id   = aws_api_gateway_resource.renew.id
  http_method   = "PUT"
  authorization = "NONE"
}

resource "aws_api_gateway_integration" "renew_put_integration" {
  rest_api_id             = aws_api_gateway_rest_api.device_api.id
  resource_id             = aws_api_gateway_resource.renew.id
  http_method             = aws_api_gateway_method.renew_put.http_method
  integration_http_method = "POST"
  type                    = "AWS_PROXY"
  uri                     = aws_lambda_function.renew_registration.invoke_arn
}

# /devices Resource (plural - for device POST requests)
resource "aws_api_gateway_resource" "devices" {
  path_part   = "devices"
  parent_id   = aws_api_gateway_rest_api.device_api.root_resource_id
  rest_api_id = aws_api_gateway_rest_api.device_api.id
}

# CORS (OPTIONS) for /devices
resource "aws_api_gateway_method" "devices_options" {
  rest_api_id   = aws_api_gateway_rest_api.device_api.id
  resource_id   = aws_api_gateway_resource.devices.id
  http_method   = "OPTIONS"
  authorization = "NONE"
}

resource "aws_api_gateway_integration" "devices_options_integration" {
  rest_api_id = aws_api_gateway_rest_api.device_api.id
  resource_id = aws_api_gateway_resource.devices.id
  http_method = aws_api_gateway_method.devices_options.http_method
  type        = "MOCK"

  request_templates = {
    "application/json" = "{\"statusCode\": 200}"
  }
}

resource "aws_api_gateway_method_response" "devices_options_response" {
  rest_api_id = aws_api_gateway_rest_api.device_api.id
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
  rest_api_id = aws_api_gateway_rest_api.device_api.id
  resource_id = aws_api_gateway_resource.devices.id
  http_method = aws_api_gateway_method.devices_options.http_method
  status_code = "200"

  response_parameters = {
    "method.response.header.Access-Control-Allow-Headers"      = "'Content-Type,X-Amz-Date,Authorization,X-Api-Key,X-Amz-Security-Token'"
    "method.response.header.Access-Control-Allow-Methods"      = "'POST,PUT,OPTIONS'"
    "method.response.header.Access-Control-Allow-Origin"       = "'*'"
    "method.response.header.Access-Control-Allow-Credentials"  = "'true'"
  }

  depends_on = [
    aws_api_gateway_integration.devices_options_integration,
    aws_api_gateway_method_response.devices_options_response
  ]
}

# PUT /devices -> Lambda: upload_device_data (requires API key, no lambda auth)
resource "aws_api_gateway_method" "devices_put" {
  rest_api_id   = aws_api_gateway_rest_api.device_api.id
  resource_id   = aws_api_gateway_resource.devices.id
  http_method   = "PUT"
  authorization = "NONE"
}

resource "aws_api_gateway_integration" "devices_put_integration" {
  rest_api_id             = aws_api_gateway_rest_api.device_api.id
  resource_id             = aws_api_gateway_resource.devices.id
  http_method             = aws_api_gateway_method.devices_put.http_method
  integration_http_method = "POST"
  type                    = "AWS_PROXY"
  uri                     = aws_lambda_function.upload_device_data.invoke_arn
}

# POST /devices -> Lambda: register_device
resource "aws_api_gateway_method" "devices_post" {
  rest_api_id   = aws_api_gateway_rest_api.device_api.id
  resource_id   = aws_api_gateway_resource.devices.id
  http_method   = "POST"
  authorization = "NONE"
}

resource "aws_api_gateway_integration" "devices_post_integration" {
  rest_api_id             = aws_api_gateway_rest_api.device_api.id
  resource_id             = aws_api_gateway_resource.devices.id
  http_method             = aws_api_gateway_method.devices_post.http_method
  integration_http_method = "POST"
  type                    = "AWS_PROXY"
  uri                     = aws_lambda_function.register_device.invoke_arn
}

# Deployment + Stage
resource "aws_api_gateway_deployment" "device_api_deployment" {
  rest_api_id = aws_api_gateway_rest_api.device_api.id

  triggers = {
    redeployment = sha1(jsonencode([
      # Integrations
      aws_api_gateway_integration.renew_put_integration.uri,
      aws_api_gateway_integration.renew_options_integration.uri,
      aws_api_gateway_integration.devices_put_integration.uri,
      aws_api_gateway_integration.devices_post_integration.uri,
      aws_api_gateway_integration.devices_options_integration.uri,

      # Methods
      aws_api_gateway_method.renew_put.authorization,
      aws_api_gateway_method.renew_options.authorization,
      aws_api_gateway_method.devices_put.authorization,
      aws_api_gateway_method.devices_post.authorization,
      aws_api_gateway_method.devices_options.authorization,


      # Permissions
      aws_lambda_permission.allow_device_api_renew_device.id,
      aws_lambda_permission.allow_device_api_device_post.id,
      aws_lambda_permission.allow_device_api_device_put.id,
    ]))
  }

  lifecycle {
    create_before_destroy = true
  }

  depends_on = [
    aws_api_gateway_integration.renew_put_integration,
    aws_api_gateway_integration.renew_options_integration,
  ]
}

resource "null_resource" "wait_for_truststore" {
  triggers = {
    instance_id = aws_instance.ca_instance.id
  }

  provisioner "local-exec" {
    command = <<-EOT
      echo "Waiting for truststore.pem to appear in S3..."
      for i in $(seq 1 40); do
        aws s3 ls s3://${aws_s3_bucket.truststore_bucket.bucket}/truststore.pem && echo "Found!" && exit 0
        echo "Attempt $i/40, retrying in 30s..."
        sleep 30
      done
      echo "Truststore never appeared, timing out"
      exit 1
    EOT
  }

  depends_on = [aws_instance.ca_instance]
}

resource "aws_api_gateway_stage" "device_api_stage" {
  deployment_id = aws_api_gateway_deployment.device_api_deployment.id
  rest_api_id   = aws_api_gateway_rest_api.device_api.id
  stage_name    = "${var.deploy_env}_trailplanner_device_api_stage"
  depends_on = [null_resource.wait_for_truststore]

}

resource "aws_lambda_permission" "allow_device_api_renew_device" {
  statement_id = "AllowDeviceAPIInvokeRenewDevice"
  action = "lambda:InvokeFunction"
  function_name = aws_lambda_function.renew_registration.function_name
  principal = "apigateway.amazonaws.com"
  source_arn = "${aws_api_gateway_rest_api.device_api.execution_arn}/*/*"
}

resource "aws_lambda_permission" "allow_device_api_device_post" {
  statement_id = "AllowDeviceAPIInvokeSendDeviceInfo"
  action = "lambda:InvokeFunction"
  function_name = aws_lambda_function.register_device.function_name
  principal = "apigateway.amazonaws.com"
  source_arn = "${aws_api_gateway_rest_api.device_api.execution_arn}/*/*"
}

resource "aws_lambda_permission" "allow_device_api_device_put" {
  statement_id = "AllowDeviceAPIInvokeSendTrailData"
  action = "lambda:InvokeFunction"
  function_name = aws_lambda_function.upload_device_data.function_name
  principal = "apigateway.amazonaws.com"
  source_arn = "${aws_api_gateway_rest_api.device_api.execution_arn}/*/*"
}

resource "aws_api_gateway_domain_name" "api_device_domain" {
  domain_name = "device${var.sub}.${var.domain}"
  regional_certificate_arn = var.acm_certificate_arn

  mutual_tls_authentication {
    truststore_uri     = "s3://${aws_s3_bucket.truststore_bucket.bucket}/truststore.pem"
  }

  endpoint_configuration {
    types = ["REGIONAL"]
  }

  security_policy = "TLS_1_2"
  endpoint_access_mode = "STRICT"
}

resource "aws_api_gateway_base_path_mapping" "api_device_mapping" {
  api_id      = aws_api_gateway_rest_api.device_api.id
  stage_name  = aws_api_gateway_stage.device_api_stage.stage_name
  domain_name = aws_api_gateway_domain_name.api_device_domain.domain_name
}
