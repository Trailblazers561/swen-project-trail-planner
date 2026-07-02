resource "null_resource" "generate_id_token" {
  count = local.local_run ? 1 : 0
  provisioner "local-exec" {
    command = "aws cognito-idp initiate-auth --region us-east-1 --auth-flow USER_PASSWORD_AUTH --client-id ${aws_cognito_user_pool_client.client.id} --auth-parameters USERNAME=${local.users["root_admin"].email},PASSWORD=${local.users["root_admin"].password} --output json > token.json"
  }

  depends_on = [aws_cognito_user_pool_client.client, aws_cognito_user.users]

  triggers = {
    token_request_time = timestamp()
  }
}

data "local_file" "cognito_token_json" {
  count = local.local_run ? 1 : 0
  filename   = "${path.module}/token.json"
  depends_on = [null_resource.generate_id_token]
}

locals {
  cognito_token = local.local_run ? jsondecode(data.local_file.cognito_token_json[0].content).AuthenticationResult.AccessToken : ""
}

# Environment file for testing (.env)
resource "local_sensitive_file" "testing_env" {
  count = local.local_run ? 1 : 0
  content = <<EOF
CLOUDFRONT_URL=http://${aws_cloudfront_distribution.s3_distribution.domain_name}
API_URL=${aws_api_gateway_stage.api_stage.invoke_url}
API_TOKEN=${local.cognito_token}
USER_PASSWORDS=${local.password}
LOCAL_RUN=true
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

resource "null_resource" "load_test_data" {
  # Yes this isn't possible for regular scenario, but when testing locally it is helpful
  count = local.test_run && local.local_run ? 1 : 0 

  triggers = {
    always_run = timestamp()
  }

  provisioner "local-exec" {
    command = "python ${local.sample_data_directory}/load_test_data.py --env ${var.deploy_env}"
  }

  depends_on = [
    aws_dynamodb_table.device_trail_log_hour_table,
    aws_dynamodb_table.device_trail_log_day_table,
    aws_dynamodb_table.device_trail_log_week_table,
    aws_dynamodb_table.device_trail_log_month_table
  ]
}