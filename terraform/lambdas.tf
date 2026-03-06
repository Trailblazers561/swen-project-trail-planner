data "archive_file" "traildata_zip" {
  type        = "zip"
  source_file = "${path.module}/${local.lambda_code_directory}/traildata.py"
  output_path = "${path.module}/${local.lambda_code_directory}/zips/traildata.zip"
}

resource "aws_lambda_function" "get_trail_data" {
  function_name = "${var.deploy_env}_traildata_get_trail_data"
  role          = aws_iam_role.lambda_iam_role.arn
  handler       = "traildata.get_trail_data"
  runtime       = "python3.12"
  filename      = "${path.module}/${local.lambda_code_directory}/zips/traildata.zip"

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
  function_name = "${var.deploy_env}_traildata_upload_trail_data"
  role          = aws_iam_role.lambda_iam_role.arn
  handler       = "traildata.upload_trail_data"
  runtime       = "python3.12"
  filename      = "${path.module}/${local.lambda_code_directory}/zips/traildata.zip"

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
  function_name = "${var.deploy_env}_traildata_upload_device_data"
  role          = aws_iam_role.lambda_iam_role.arn
  handler       = "traildata.upload_device_data"
  runtime       = "python3.12"
  filename      = "${path.module}/${local.lambda_code_directory}/zips/traildata.zip"

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

resource "aws_lambda_function" "update_trail_metadata" {
  function_name = "${var.deploy_env}_traildata_update_trail_metadata"
  role          = aws_iam_role.lambda_iam_role.arn
  handler       = "traildata.update_trail_metadata"
  runtime       = "python3.12"
  filename      = "${path.module}/${local.lambda_code_directory}/zips/traildata.zip"

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

resource "aws_lambda_function" "update_device_trail_association" {
  function_name = "${var.deploy_env}_traildata_update_device_trail_association"
  role          = aws_iam_role.lambda_iam_role.arn
  handler       = "traildata.update_device_trail_association"
  runtime       = "python3.12"
  filename      = "${path.module}/${local.lambda_code_directory}/zips/traildata.zip"

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

resource "aws_lambda_function" "get_trail_metadata" {
  function_name = "${var.deploy_env}_traildata_get_trail_metadata"
  role          = aws_iam_role.lambda_iam_role.arn
  handler       = "traildata.get_trail_metadata"
  runtime       = "python3.12"
  filename      = "${path.module}/${local.lambda_code_directory}/zips/traildata.zip"

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

resource "aws_lambda_function" "get_device_metadata" {
  function_name = "${var.deploy_env}_traildata_get_device_metadata"
  role          = aws_iam_role.lambda_iam_role.arn
  handler       = "traildata.get_device_metadata"
  runtime       = "python3.12"
  filename      = "${path.module}/${local.lambda_code_directory}/zips/traildata.zip"

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

resource "aws_lambda_function" "get_trail_groups" {
  function_name = "${var.deploy_env}_traildata_get_trail_groups"
  role          = aws_iam_role.lambda_iam_role.arn
  handler       = "traildata.get_trail_groups"
  runtime       = "python3.12"
  filename      = "${path.module}/${local.lambda_code_directory}/zips/traildata.zip"

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

resource "aws_lambda_function" "delete_trail" {
  function_name = "${var.deploy_env}_traildata_delete_trail"
  role          = aws_iam_role.lambda_iam_role.arn
  handler       = "traildata.delete_trail"
  runtime       = "python3.12"
  filename      = "${path.module}/${local.lambda_code_directory}/zips/traildata.zip"

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

resource "aws_lambda_function" "create_trail" {
  function_name = "${var.deploy_env}_traildata_create_trail"
  role          = aws_iam_role.lambda_iam_role.arn
  handler       = "traildata.create_trail"
  runtime       = "python3.12"
  filename      = "${path.module}/${local.lambda_code_directory}/zips/traildata.zip"

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

# Map of function names to Lambda function resources
locals {
  api_lambda_functions = {
    "traildata_upload_trail_data"            = aws_lambda_function.upload_trail_data
    "traildata_get_trail_data"               = aws_lambda_function.get_trail_data
    "traildata_upload_device_data"           = aws_lambda_function.upload_device_data
    "traildata_update_trail_metadata"        = aws_lambda_function.update_trail_metadata
    "traildata_create_trail"                  = aws_lambda_function.create_trail
    "traildata_update_device_trail_association" = aws_lambda_function.update_device_trail_association
    "traildata_get_trail_metadata"           = aws_lambda_function.get_trail_metadata
    "traildata_get_device_metadata"          = aws_lambda_function.get_device_metadata
    "traildata_get_trail_groups"             = aws_lambda_function.get_trail_groups
    "traildata_delete_trail"                 = aws_lambda_function.delete_trail
    "traildata_export_csv"                     = aws_lambda_function.export_csv
  }
}

resource "aws_lambda_permission" "allow_apigateway_all_functions" {
  for_each = local.api_lambda_functions

  statement_id  = "AllowExecutionFromAPIGateway-${each.key}"
  action        = "lambda:InvokeFunction"
  function_name = each.value.function_name
  principal     = "apigateway.amazonaws.com"

  source_arn = "${aws_api_gateway_rest_api.api.execution_arn}/*/*"
}

data "archive_file" "export_csv_zip" {
  type        = "zip"
  source_file = "${path.module}/${local.lambda_code_directory}/export_csv.py"
  output_path = "${path.module}/${local.lambda_code_directory}/zips/export_csv.zip"
}

resource "aws_lambda_function" "export_csv" {
  function_name = "${var.deploy_env}_export_csv"
  role          = aws_iam_role.lambda_iam_role.arn
  handler       = "export_csv.create_and_fill_csv"
  runtime       = "python3.12"
  filename      = "${path.module}/${local.lambda_code_directory}/zips/export_csv.zip"
  code_sha256   = data.archive_file.export_csv_zip.output_base64sha256
  timeout       = 30

  environment {
    variables = {
      TRAIL_LOGS_TABLE      = aws_dynamodb_table.trail_device_logs.name
      TRAIL_METADATA_TABLE  = aws_dynamodb_table.trail_metadata.name
      DEVICE_METADATA_TABLE = aws_dynamodb_table.device_metadata.name
      TRAIL_GROUPS_TABLE    = aws_dynamodb_table.trail_groups.name
      TRAIL_S3_BUCKET       = aws_s3_bucket.csv_bucket.bucket
    }
  }
  depends_on = [
    aws_iam_role.lambda_iam_role,
    aws_dynamodb_table.trail_device_logs,
    aws_dynamodb_table.device_metadata,
    aws_dynamodb_table.trail_metadata,
    aws_dynamodb_table.trail_groups
    ]
}

resource "aws_cloudwatch_event_rule" "daily_cleanup" {
  name                = "daily_cleanup"
  schedule_expression = "rate(1 day)"
}

resource "aws_cloudwatch_event_target" "trigger_cleanup" {
  rule      = aws_cloudwatch_event_rule.daily_cleanup.name
  target_id = "lambda"
  arn       = aws_lambda_function.cleanup_lambda.arn
}

resource "aws_lambda_permission" "allow_cloudwatch" {
  statement_id  = "AllowExecutionFromCloudWatch"
  action        = "lambda:InvokeFunction"
  function_name = aws_lambda_function.cleanup_lambda.function_name
  principal     = "events.amazonaws.com"
  source_arn    = aws_cloudwatch_event_rule.daily_cleanup.arn
}

data "archive_file" "cleanup_lambda_zip" {
  type        = "zip"
  source_file = "${path.module}/${local.lambda_code_directory}/cleanup_lambda.py"
  output_path = "${path.module}/${local.lambda_code_directory}/zips/cleanup_lambda.zip"
}

resource "aws_lambda_function" "cleanup_lambda" {
  function_name = "cleanup_old_frames"
  role          = aws_iam_role.lambda_iam_role.arn
  handler       = "delete_frames.lambda_handler"
  runtime       = "python3.11"

  filename      = "${path.module}/${local.lambda_code_directory}/zips/cleanup_lambda.zip"
  code_sha256   = data.archive_file.cleanup_lambda_zip.output_base64sha256

  environment {
    variables = {
      BUCKET_NAME = aws_s3_bucket.csv_bucket.bucket
    }
  }
}
