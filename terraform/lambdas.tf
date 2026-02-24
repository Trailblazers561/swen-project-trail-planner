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
  code_sha256 = data.archive_file.traildata_zip.output_base64sha256

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
  code_sha256 = data.archive_file.traildata_zip.output_base64sha256

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
  code_sha256 = data.archive_file.traildata_zip.output_base64sha256

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
  code_sha256 = data.archive_file.traildata_zip.output_base64sha256

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
  code_sha256 = data.archive_file.traildata_zip.output_base64sha256

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
  code_sha256 = data.archive_file.traildata_zip.output_base64sha256

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
  code_sha256 = data.archive_file.traildata_zip.output_base64sha256

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
  code_sha256 = data.archive_file.traildata_zip.output_base64sha256

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
  code_sha256 = data.archive_file.traildata_zip.output_base64sha256

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
  code_sha256 = data.archive_file.traildata_zip.output_base64sha256

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
  lambda_functions = {
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
  }
}

resource "aws_lambda_permission" "allow_apigateway_all_functions" {
  for_each = local.lambda_functions

  statement_id  = "AllowExecutionFromAPIGateway-${each.key}"
  action        = "lambda:InvokeFunction"
  function_name = each.value.function_name
  principal     = "apigateway.amazonaws.com"

  source_arn = "${aws_api_gateway_rest_api.api.execution_arn}/*/*"
}

data "archive_file" "simulate_data_zip" {
  type        = "zip"
  source_file = "${path.module}/${local.lambda_code_directory}/simulate_data.py"
  output_path = "${path.module}/${local.lambda_code_directory}/zips/simulate_data.zip"
}

resource "aws_lambda_function" "simulate_data" {
  function_name = "${var.deploy_env}_simulate_traildata2"
  role          = aws_iam_role.lambda_iam_role.arn
  handler       = "simulate_data.simulate_data"
  runtime       = "python3.12"
  filename      = "${path.module}/${local.lambda_code_directory}/zips/simulate_data.zip"
  code_sha256 = data.archive_file.simulate_data_zip.output_base64sha256
  timeout = 30

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

resource "aws_cloudwatch_event_rule" "trigger_simulate_data" {
    name = "${var.deploy_env}_trigger_simulate_data"
    schedule_expression = "cron(0 3 * * ? *)" # This runs at 10:00pm / 11:00pm EST
}

resource "aws_cloudwatch_event_target" "trigger_lambda_every_day" {
    rule = aws_cloudwatch_event_rule.trigger_simulate_data.name
    target_id = "${var.deploy_env}_simulate_data_event"
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
  # Change this value to trigger lambda on next apply
  input = "simulate-data"

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