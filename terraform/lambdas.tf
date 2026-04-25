# Simulate Data Lambda
data "archive_file" "simulate_data_zip" {
  type        = "zip"
  source_file = "${path.module}/${local.lambda_code_directory}/simulate_data.py"
  output_path = "${path.module}/${local.lambda_code_directory}/zips/simulate_data.zip"
}

resource "aws_lambda_function" "simulate_data" {
  function_name = "${var.deploy_env}_trailplanner_simulate_data"
  role          = aws_iam_role.lambda_iam_role.arn
  handler       = "simulate_data.simulate_data"
  runtime       = "python3.12"
  filename      = "${path.module}/${local.lambda_code_directory}/zips/simulate_data.zip"
  code_sha256 = data.archive_file.simulate_data_zip.output_base64sha256
  timeout = 30
  environment {
    variables = {
      DEVICE_TRAIL_LOG_HOUR_TABLE      = aws_dynamodb_table.device_trail_log_hour_table.name
      DEVICE_TRAIL_LOG_DAY_TABLE      = aws_dynamodb_table.device_trail_log_day_table.name
      DEVICE_TRAIL_LOG_WEEK_TABLE      = aws_dynamodb_table.device_trail_log_week_table.name
      DEVICE_TRAIL_LOG_MONTH_TABLE      = aws_dynamodb_table.device_trail_log_month_table.name
      TRAIL_TABLE = aws_dynamodb_table.trail_table.name
      DEVICE_TABLE = aws_dynamodb_table.device_table.name
      DEVICE_TRAIL_TABLE = aws_dynamodb_table.device_trail_table.name
      TRAIL_GROUP_TABLE    = aws_dynamodb_table.trail_group_table.name
    }
  }
}

resource "aws_cloudwatch_event_rule" "trigger_simulate_data" {
    name = "${var.deploy_env}_trailplanner_trigger_simulate_data"
    schedule_expression = "cron(0 3 * * ? *)" # This runs at 10:00pm / 11:00pm EST
}

resource "aws_cloudwatch_event_target" "trigger_lambda_every_day" {
    count = local.test_run ? 0 : 1
    rule = aws_cloudwatch_event_rule.trigger_simulate_data.name
    target_id = "${var.deploy_env}_trailplanner_simulate_data_event"
    arn = aws_lambda_function.simulate_data.arn
}

resource "aws_lambda_permission" "allow_invoke" {
    action = "lambda:InvokeFunction"
    function_name = aws_lambda_function.simulate_data.function_name
    principal = "events.amazonaws.com"
    source_arn = aws_cloudwatch_event_rule.trigger_simulate_data.arn
}

locals {
  time = timestamp()
  simulation_timestamp = (formatdate("HH", local.time) >= 3 ? local.time : timeadd(local.time, "-24h"))
  payloads = {
    seven = jsonencode({time=formatdate("YYYY-MM-DD", timeadd(local.simulation_timestamp, "-144h"))})
    six = jsonencode({time=formatdate("YYYY-MM-DD", timeadd(local.simulation_timestamp, "-120h"))})
    five = jsonencode({time=formatdate("YYYY-MM-DD", timeadd(local.simulation_timestamp, "-96h"))})
    four = jsonencode({time=formatdate("YYYY-MM-DD", timeadd(local.simulation_timestamp, "-72h"))})
    three = jsonencode({time=formatdate("YYYY-MM-DD", timeadd(local.simulation_timestamp, "-48h"))})
    two = jsonencode({time=formatdate("YYYY-MM-DD", timeadd(local.simulation_timestamp, "-24h"))})
    one = jsonencode({time=formatdate("YYYY-MM-DD", local.simulation_timestamp)})
  }
}

action "aws_lambda_invoke" "invoke_simulate_data" {
  for_each = local.payloads
  config {
    function_name = aws_lambda_function.simulate_data.function_name
    payload = each.value
  }
}

resource "terraform_data" "invoke_simulate_data" {
  count = local.test_run ? 0 : 1
  # Change this value to trigger lambda on next apply
  input = "simulate-data-again"

  lifecycle {
    action_trigger {
      events  = [after_create, after_update]
      actions = [
        action.aws_lambda_invoke.invoke_simulate_data["seven"],
        action.aws_lambda_invoke.invoke_simulate_data["six"],
        action.aws_lambda_invoke.invoke_simulate_data["five"],
        action.aws_lambda_invoke.invoke_simulate_data["four"],
        action.aws_lambda_invoke.invoke_simulate_data["three"],
        action.aws_lambda_invoke.invoke_simulate_data["two"],
        action.aws_lambda_invoke.invoke_simulate_data["one"]
      ]
    }
  }
}

# Daily Cleanup Lambda
data "archive_file" "cleanup_lambda_zip" {
  type        = "zip"
  source_file = "${path.module}/${local.lambda_code_directory}/cleanup_lambda.py"
  output_path = "${path.module}/${local.lambda_code_directory}/zips/cleanup_lambda.zip"
}

resource "aws_lambda_function" "cleanup_lambda" {
  function_name = "${var.deploy_env}_trailplanner_cleanup_csv_bucket"
  role          = aws_iam_role.lambda_iam_role.arn
  handler       = "cleanup_lambda.cleanup"
  runtime       = "python3.11"

  filename      = "${path.module}/${local.lambda_code_directory}/zips/cleanup_lambda.zip"
  code_sha256   = data.archive_file.cleanup_lambda_zip.output_base64sha256

  environment {
    variables = {
      BUCKET_NAME = aws_s3_bucket.csv_bucket.bucket
    }
  }
}

resource "aws_cloudwatch_event_rule" "csv_bucket_daily_cleanup" {
  name                = "${var.deploy_env}_trailplanner_daily_cleanup"
  schedule_expression = "rate(1 day)"
}

resource "aws_cloudwatch_event_target" "trigger_cleanup" {
  rule      = aws_cloudwatch_event_rule.csv_bucket_daily_cleanup.name
  target_id = "${var.deploy_env}_trailplanner_cleanup_event"
  arn       = aws_lambda_function.cleanup_lambda.arn
}

resource "aws_lambda_permission" "allow_cloudwatch" {
  statement_id  = "AllowExecutionFromCloudWatch"
  action        = "lambda:InvokeFunction"
  function_name = aws_lambda_function.cleanup_lambda.function_name
  principal     = "events.amazonaws.com"
  source_arn    = aws_cloudwatch_event_rule.csv_bucket_daily_cleanup.arn
}

# Confirm User Lambda To Put User In "User" User Group After Verification 
data "archive_file" "confirm_user_lambda_zip" {
  type        = "zip"
  source_file = "${path.module}/${local.lambda_code_directory}/confirm_user.py"
  output_path = "${path.module}/${local.lambda_code_directory}/zips/confirm_user.zip"
}

resource "aws_lambda_function" "confirm_user" {
  function_name = "${var.deploy_env}_trailplanner_confirm_user"
  role          = aws_iam_role.lambda_iam_role.arn
  handler       = "confirm_user.confirm_user"
  runtime       = "python3.12"
  filename      = "${path.module}/${local.lambda_code_directory}/zips/confirm_user.zip"
  code_sha256 = data.archive_file.confirm_user_lambda_zip.output_base64sha256
}

resource "aws_lambda_permission" "allow_cognito" {
  statement_id  = "AllowExecutionFromCognito"
  action        = "lambda:InvokeFunction"
  function_name = aws_lambda_function.confirm_user.function_name
  principal     = "cognito-idp.amazonaws.com"
}