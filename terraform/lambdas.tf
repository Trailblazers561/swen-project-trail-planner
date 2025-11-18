data "archive_file" "traildata_zip" {
  type        = "zip"
  source_file = "${path.module}/../lambdas/traildata.py"
  output_path = "${path.module}/../lambdas/zips/traildata.zip"
}

resource "aws_lambda_function" "get_trail_data" {
  function_name = "traildata_get_trail_data"
  role          = aws_iam_role.lambda_iam_role.arn
  handler       = "traildata.get_trail_data"
  runtime       = "python3.12"
  filename      = "${path.module}/../lambdas/zips/traildata.zip"

  environment {
    variables = {
      TRAIL_LOGS_TABLE      = aws_dynamodb_table.trail_device_logs.name
      TRAIL_METADATA_TABLE  = aws_dynamodb_table.trail_metadata.name
      DEVICE_METADATA_TABLE = aws_dynamodb_table.device_metadata.name
      TRAIL_GROUPS_TABLE    = aws_dynamodb_table.trail_groups.name
    }
  }

  depends_on = [aws_iam_role.lambda_iam_role]
}

resource "aws_lambda_function" "upload_trail_data" {
  function_name = "traildata_upload_trail_data"
  role          = aws_iam_role.lambda_iam_role.arn
  handler       = "traildata.upload_trail_data"
  runtime       = "python3.12"
  filename      = "${path.module}/../lambdas/zips/traildata.zip"

  environment {
    variables = {
      TRAIL_LOGS_TABLE      = aws_dynamodb_table.trail_device_logs.name
      TRAIL_METADATA_TABLE  = aws_dynamodb_table.trail_metadata.name
      DEVICE_METADATA_TABLE = aws_dynamodb_table.device_metadata.name
      TRAIL_GROUPS_TABLE    = aws_dynamodb_table.trail_groups.name
    }
  }

  depends_on = [aws_iam_role.lambda_iam_role]
}

resource "aws_lambda_function" "upload_device_data" {
  function_name = "traildata_upload_device_data"
  role          = aws_iam_role.lambda_iam_role.arn
  handler       = "traildata.upload_device_data"
  runtime       = "python3.12"
  filename      = "${path.module}/../lambdas/zips/traildata.zip"

  environment {
    variables = {
      TRAIL_LOGS_TABLE      = aws_dynamodb_table.trail_device_logs.name
      TRAIL_METADATA_TABLE  = aws_dynamodb_table.trail_metadata.name
      DEVICE_METADATA_TABLE = aws_dynamodb_table.device_metadata.name
      TRAIL_GROUPS_TABLE    = aws_dynamodb_table.trail_groups.name
    }
  }

  depends_on = [aws_iam_role.lambda_iam_role]
}

variable "lambda_function_names" {
  default = [
    "traildata_upload_trail_data",
    "traildata_get_trail_data",
    "traildata_upload_device_data",
  ]
}

resource "aws_lambda_permission" "allow_apigateway_all_functions" {
  for_each = toset(var.lambda_function_names)

  statement_id  = "AllowExecutionFromAPIGateway-${each.value}"
  action        = "lambda:InvokeFunction"
  function_name = each.value
  principal     = "apigateway.amazonaws.com"

  source_arn = "${aws_api_gateway_rest_api.api.execution_arn}/*/*"
}