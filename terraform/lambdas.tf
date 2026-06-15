data "archive_file" "traildata_zip" {
  type        = "zip"
  source_file = "${path.module}/${local.lambda_code_directory}/traildata.py"
  output_path = "${path.module}/${local.lambda_code_directory}/zips/traildata.zip"
}

data "archive_file" "register_device_zip" {
  type        = "zip"
  source_file = "${path.module}/${local.lambda_code_directory}/register_device.py"
  output_path = "${path.module}/${local.lambda_code_directory}/zips/register_device.zip"
}

resource "aws_lambda_function" "set_device_blocked" {
  function_name = "${var.deploy_env}_traildata_set_device_blocked"
  role          = aws_iam_role.lambda_iam_role.arn
  handler       = "traildata.set_device_blocked"
  runtime       = "python3.12"
  filename      = "${path.module}/${local.lambda_code_directory}/zips/traildata.zip"
  code_sha256 = data.archive_file.traildata_zip.output_base64sha256
  timeout = 10

  environment {
    variables = {
      REGISTRATION_TABLE = aws_dynamodb_table.registration_table.name
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

resource "aws_lambda_function" "set_device_archived" {
  function_name = "${var.deploy_env}_traildata_set_device_archived"
  role          = aws_iam_role.lambda_iam_role.arn
  handler       = "traildata.set_device_archived"
  runtime       = "python3.12"
  filename      = "${path.module}/${local.lambda_code_directory}/zips/traildata.zip"
  code_sha256 = data.archive_file.traildata_zip.output_base64sha256
  timeout = 10

  environment {
    variables = {
      REGISTRATION_TABLE = aws_dynamodb_table.registration_table.name
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

resource "aws_lambda_function" "delete_registration" {
  function_name = "${var.deploy_env}_traildata_delete_registration"
  role          = aws_iam_role.lambda_iam_role.arn
  handler       = "traildata.delete_registration"
  runtime       = "python3.12"
  filename      = "${path.module}/${local.lambda_code_directory}/zips/traildata.zip"
  code_sha256 = data.archive_file.traildata_zip.output_base64sha256
  timeout = 10

  environment {
    variables = {
      REGISTRATION_TABLE = aws_dynamodb_table.registration_table.name
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

resource "aws_lambda_function" "edit_registration" {
  function_name = "${var.deploy_env}_traildata_edit_registration"
  role          = aws_iam_role.lambda_iam_role.arn
  handler       = "traildata.edit_registration"
  runtime       = "python3.12"
  filename      = "${path.module}/${local.lambda_code_directory}/zips/traildata.zip"
  code_sha256 = data.archive_file.traildata_zip.output_base64sha256
  timeout = 10

  environment {
    variables = {
      REGISTRATION_TABLE = aws_dynamodb_table.registration_table.name
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

resource "aws_lambda_function" "get_registrations" {
  function_name = "${var.deploy_env}_traildata_get_registrations"
  role          = aws_iam_role.lambda_iam_role.arn
  handler       = "traildata.get_registrations"
  runtime       = "python3.12"
  filename      = "${path.module}/${local.lambda_code_directory}/zips/traildata.zip"
  code_sha256 = data.archive_file.traildata_zip.output_base64sha256
  timeout = 10

  environment {
    variables = {
      REGISTRATION_TABLE = aws_dynamodb_table.registration_table.name
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

resource "aws_lambda_function" "pre_register_device" {
  function_name = "${var.deploy_env}_traildata_pre_register_device"
  role          = aws_iam_role.lambda_iam_role.arn
  handler       = "traildata.pre_register_device"
  runtime       = "python3.12"
  filename      = "${path.module}/${local.lambda_code_directory}/zips/traildata.zip"
  code_sha256 = data.archive_file.traildata_zip.output_base64sha256
  timeout = 10

  environment {
    variables = {
      REGISTRATION_TABLE = aws_dynamodb_table.registration_table.name
      DEVICE_TRAIL_LOG_HOUR_TABLE      = aws_dynamodb_table.device_trail_log_hour_table.name
      DEVICE_TRAIL_LOG_DAY_TABLE      = aws_dynamodb_table.device_trail_log_day_table.name
      DEVICE_TRAIL_LOG_WEEK_TABLE      = aws_dynamodb_table.device_trail_log_week_table.name
      DEVICE_TRAIL_LOG_MONTH_TABLE      = aws_dynamodb_table.device_trail_log_month_table.name
      TRAIL_TABLE = aws_dynamodb_table.trail_table.name
      DEVICE_TABLE = aws_dynamodb_table.device_table.name
      DEVICE_TRAIL_TABLE = aws_dynamodb_table.device_trail_table.name
      TRAIL_GROUP_TABLE    = aws_dynamodb_table.trail_group_table.name
      CERTIFICATE_AUTHORITY_URL = "https://${aws_instance.ca_instance.private_ip}:9000"
    }
  }

  vpc_config {
    security_group_ids = [aws_security_group.lambda_sg.id]
    subnet_ids = [aws_subnet.private_subnet.id]
  }
}

resource "aws_lambda_function" "device_cert_registration" {
  function_name = "${var.deploy_env}_traildata_device_registration"
  role          = aws_iam_role.lambda_iam_role.arn
  handler       = "register_device.register_device"
  runtime       = "python3.12"
  filename      = "${path.module}/${local.lambda_code_directory}/zips/register_device.zip"
  code_sha256 = data.archive_file.register_device_zip.output_base64sha256
  timeout = 10

  environment {
    variables = {
      REGISTRATION_TABLE = aws_dynamodb_table.registration_table.name
      DEVICE_TRAIL_LOG_HOUR_TABLE      = aws_dynamodb_table.device_trail_log_hour_table.name
      DEVICE_TRAIL_LOG_DAY_TABLE      = aws_dynamodb_table.device_trail_log_day_table.name
      DEVICE_TRAIL_LOG_WEEK_TABLE      = aws_dynamodb_table.device_trail_log_week_table.name
      DEVICE_TRAIL_LOG_MONTH_TABLE      = aws_dynamodb_table.device_trail_log_month_table.name
      TRAIL_TABLE = aws_dynamodb_table.trail_table.name
      DEVICE_TABLE = aws_dynamodb_table.device_table.name
      DEVICE_TRAIL_TABLE = aws_dynamodb_table.device_trail_table.name
      TRAIL_GROUP_TABLE    = aws_dynamodb_table.trail_group_table.name
      CERTIFICATE_AUTHORITY_URL = "https://${aws_instance.ca_instance.private_ip}:9000"
    }
  }

  vpc_config {
    security_group_ids = [aws_security_group.lambda_sg.id]
    subnet_ids = [aws_subnet.private_subnet.id]
  }
}


resource "aws_lambda_function" "register_device" {
  function_name = "${var.deploy_env}_traildata_register_device"
  role          = aws_iam_role.lambda_iam_role.arn
  handler       = "traildata.register_device"
  runtime       = "python3.12"
  filename      = "${path.module}/${local.lambda_code_directory}/zips/traildata.zip"
  code_sha256 = data.archive_file.traildata_zip.output_base64sha256
  timeout = 10

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

resource "aws_lambda_function" "get_trail_data" {
  function_name = "${var.deploy_env}_traildata_get_trail_data"
  role          = aws_iam_role.lambda_iam_role.arn
  handler       = "traildata.get_trail_data"
  runtime       = "python3.12"
  filename      = "${path.module}/${local.lambda_code_directory}/zips/traildata.zip"
  code_sha256 = data.archive_file.traildata_zip.output_base64sha256
  timeout = 10

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

resource "aws_lambda_function" "upload_trail_data" {
  function_name = "${var.deploy_env}_traildata_upload_trail_data"
  role          = aws_iam_role.lambda_iam_role.arn
  handler       = "traildata.upload_trail_data"
  runtime       = "python3.12"
  filename      = "${path.module}/${local.lambda_code_directory}/zips/traildata.zip"
  code_sha256 = data.archive_file.traildata_zip.output_base64sha256

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

resource "aws_lambda_function" "upload_device_data" {
  function_name = "${var.deploy_env}_traildata_upload_device_data"
  role          = aws_iam_role.lambda_iam_role.arn
  handler       = "traildata.upload_device_data"
  runtime       = "python3.12"
  filename      = "${path.module}/${local.lambda_code_directory}/zips/traildata.zip"
  code_sha256 = data.archive_file.traildata_zip.output_base64sha256

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

resource "aws_lambda_function" "update_trail_metadata" {
  function_name = "${var.deploy_env}_traildata_update_trail_metadata"
  role          = aws_iam_role.lambda_iam_role.arn
  handler       = "traildata.update_trail_metadata"
  runtime       = "python3.12"
  filename      = "${path.module}/${local.lambda_code_directory}/zips/traildata.zip"
  code_sha256 = data.archive_file.traildata_zip.output_base64sha256

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

resource "aws_lambda_function" "update_device_trail_association" {
  function_name = "${var.deploy_env}_traildata_update_device_trail_association"
  role          = aws_iam_role.lambda_iam_role.arn
  handler       = "traildata.update_device_trail_association"
  runtime       = "python3.12"
  filename      = "${path.module}/${local.lambda_code_directory}/zips/traildata.zip"
  code_sha256 = data.archive_file.traildata_zip.output_base64sha256

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

resource "aws_lambda_function" "get_trail_metadata" {
  function_name = "${var.deploy_env}_traildata_get_trail_metadata"
  role          = aws_iam_role.lambda_iam_role.arn
  handler       = "traildata.get_trail_metadata"
  runtime       = "python3.12"
  filename      = "${path.module}/${local.lambda_code_directory}/zips/traildata.zip"
  code_sha256 = data.archive_file.traildata_zip.output_base64sha256

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

resource "aws_lambda_function" "get_device_metadata" {
  function_name = "${var.deploy_env}_traildata_get_device_metadata"
  role          = aws_iam_role.lambda_iam_role.arn
  handler       = "traildata.get_device_metadata"
  runtime       = "python3.12"
  filename      = "${path.module}/${local.lambda_code_directory}/zips/traildata.zip"
  code_sha256 = data.archive_file.traildata_zip.output_base64sha256

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

resource "aws_lambda_function" "get_trail_group_metadata" {
  function_name = "${var.deploy_env}_traildata_get_trail_group_metadata"
  role          = aws_iam_role.lambda_iam_role.arn
  handler       = "traildata.get_trail_group_metadata"
  runtime       = "python3.12"
  filename      = "${path.module}/${local.lambda_code_directory}/zips/traildata.zip"
  code_sha256 = data.archive_file.traildata_zip.output_base64sha256

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

resource "aws_lambda_function" "delete_trail" {
  function_name = "${var.deploy_env}_traildata_delete_trail"
  role          = aws_iam_role.lambda_iam_role.arn
  handler       = "traildata.delete_trail"
  runtime       = "python3.12"
  filename      = "${path.module}/${local.lambda_code_directory}/zips/traildata.zip"
  code_sha256 = data.archive_file.traildata_zip.output_base64sha256

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

resource "aws_lambda_function" "create_trail" {
  function_name = "${var.deploy_env}_traildata_create_trail"
  role          = aws_iam_role.lambda_iam_role.arn
  handler       = "traildata.create_trail"
  runtime       = "python3.12"
  filename      = "${path.module}/${local.lambda_code_directory}/zips/traildata.zip"
  code_sha256 = data.archive_file.traildata_zip.output_base64sha256

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

resource "aws_lambda_function" "delete_trail_group" {
  function_name = "${var.deploy_env}_traildata_delete_trail_group"
  role          = aws_iam_role.lambda_iam_role.arn
  handler       = "traildata.delete_trail_group"
  runtime       = "python3.12"
  filename      = "${path.module}/${local.lambda_code_directory}/zips/traildata.zip"
  code_sha256 = data.archive_file.traildata_zip.output_base64sha256

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

# Map of function names to Lambda function resources
locals {
  api_lambda_functions = {
    "lambda_authorizer"                         = aws_lambda_function.lambda_authorizer
    "traildata_upload_trail_data"            = aws_lambda_function.upload_trail_data
    "traildata_get_trail_data"               = aws_lambda_function.get_trail_data
    "traildata_register_device"               = aws_lambda_function.register_device
    "traildata_upload_device_data"           = aws_lambda_function.upload_device_data
    "traildata_update_trail_metadata"        = aws_lambda_function.update_trail_metadata
    "traildata_create_trail"                  = aws_lambda_function.create_trail
    "traildata_update_device_trail_association" = aws_lambda_function.update_device_trail_association
    "traildata_get_trail_metadata"           = aws_lambda_function.get_trail_metadata
    "traildata_get_device_metadata"          = aws_lambda_function.get_device_metadata
    "traildata_get_trail_group_metadata"             = aws_lambda_function.get_trail_group_metadata
    "traildata_delete_trail"                 = aws_lambda_function.delete_trail
    "traildata_delete_trail_group"        = aws_lambda_function.delete_trail_group
    "traildata_export_csv"                     = aws_lambda_function.export_csv
    "traildata_import_csv"                     = aws_lambda_function.import_csv
    "traildata_generate_csv_upload_url"        = aws_lambda_function.generate_csv_upload_url
    "get_users"                                     = aws_lambda_function.get_users
    "change_user_group"                      = aws_lambda_function.change_user_group
    "traildata_pre_register_device"               = aws_lambda_function.pre_register_device
    "traildata_get_registrations"    = aws_lambda_function.get_registrations
    "traildata_delete_registration"  = aws_lambda_function.delete_registration
    "traildata_edit_registration"  = aws_lambda_function.edit_registration
    "traildata_set_device_blocked"   = aws_lambda_function.set_device_blocked
    "traildata_set_device_archived"   = aws_lambda_function.set_device_archived
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

data "archive_file" "simulate_data_zip" {
  type        = "zip"
  source_file = "${path.module}/${local.lambda_code_directory}/simulate_data.py"
  output_path = "${path.module}/${local.lambda_code_directory}/zips/simulate_data.zip"
}

resource "aws_lambda_function" "simulate_data" {
  function_name = "${var.deploy_env}_simulate_traildata"
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
      DEVICE_TRAIL_LOG_HOUR_TABLE      = aws_dynamodb_table.device_trail_log_hour_table.name
      DEVICE_TRAIL_LOG_DAY_TABLE      = aws_dynamodb_table.device_trail_log_day_table.name
      DEVICE_TRAIL_LOG_WEEK_TABLE      = aws_dynamodb_table.device_trail_log_week_table.name
      DEVICE_TRAIL_LOG_MONTH_TABLE      = aws_dynamodb_table.device_trail_log_month_table.name
      TRAIL_TABLE = aws_dynamodb_table.trail_table.name
      DEVICE_TABLE = aws_dynamodb_table.device_table.name
      DEVICE_TRAIL_TABLE = aws_dynamodb_table.device_trail_table.name
      TRAIL_GROUP_TABLE    = aws_dynamodb_table.trail_group_table.name
      TRAIL_S3_BUCKET       = aws_s3_bucket.csv_bucket.bucket
    }
  }
}

data "archive_file" "import_csv_zip" {
  type        = "zip"
  source_file = "${path.module}/${local.lambda_code_directory}/import_csv.py"
  output_path = "${path.module}/${local.lambda_code_directory}/zips/import_csv.zip"
}

resource "aws_lambda_function" "import_csv" {
  function_name = "${var.deploy_env}_import_csv"
  role          = aws_iam_role.lambda_iam_role.arn
  handler       = "import_csv.parse_csv_and_export_data"
  runtime       = "python3.12"
  filename      = "${path.module}/${local.lambda_code_directory}/zips/import_csv.zip"
  code_sha256   = data.archive_file.import_csv_zip.output_base64sha256
  timeout       = 600

  environment {
    variables = {
      DEVICE_TRAIL_LOG_HOUR_TABLE      = aws_dynamodb_table.device_trail_log_hour_table.name
      DEVICE_TRAIL_LOG_DAY_TABLE      = aws_dynamodb_table.device_trail_log_day_table.name
      DEVICE_TRAIL_LOG_WEEK_TABLE      = aws_dynamodb_table.device_trail_log_week_table.name
      DEVICE_TRAIL_LOG_MONTH_TABLE      = aws_dynamodb_table.device_trail_log_month_table.name
      TRAIL_S3_BUCKET       = aws_s3_bucket.csv_bucket.bucket
    }
  }
}

data "archive_file" "generate_csv_upload_url_zip" {
  type        = "zip"
  source_file = "${path.module}/${local.lambda_code_directory}/generate_csv_upload_url.py"
  output_path = "${path.module}/${local.lambda_code_directory}/zips/generate_csv_upload_url.zip"
}

resource "aws_lambda_function" "generate_csv_upload_url" {
  function_name = "${var.deploy_env}_generate_csv_upload_url"
  role          = aws_iam_role.lambda_iam_role.arn
  handler       = "generate_csv_upload_url.generate_url"
  runtime       = "python3.12"
  filename      = "${path.module}/${local.lambda_code_directory}/zips/generate_csv_upload_url.zip"
  code_sha256   = data.archive_file.generate_csv_upload_url_zip.output_base64sha256
  timeout       = 3

  environment {
    variables = {
      TRAIL_S3_BUCKET       = aws_s3_bucket.csv_bucket.bucket
    }
  }
}

resource "aws_cloudwatch_event_rule" "daily_cleanup" {
  name                = "${var.deploy_env}_daily_cleanup"
  schedule_expression = "rate(1 day)"
}

resource "aws_cloudwatch_event_target" "trigger_cleanup" {
  rule      = aws_cloudwatch_event_rule.daily_cleanup.name
  target_id = "${var.deploy_env}_cleanup_event"
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
  function_name = "${var.deploy_env}_cleanup_csv_bucket"
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

# Lambdas for /users API endpoint
data "archive_file" "user_management_zip" {
  type        = "zip"
  source_file = "${path.module}/${local.lambda_code_directory}/user_management.py"
  output_path = "${path.module}/${local.lambda_code_directory}/zips/user_management.zip"
}

resource "aws_lambda_function" "get_users" {
  function_name = "${var.deploy_env}_get_users"
  role          = aws_iam_role.lambda_iam_role.arn
  handler       = "user_management.get_users"
  runtime       = "python3.12"
  filename      = "${path.module}/${local.lambda_code_directory}/zips/user_management.zip"
  code_sha256 = data.archive_file.traildata_zip.output_base64sha256

  environment {
    variables = {
      COGNITO_USER_POOL_ID = aws_cognito_user_pool.user_pool.id
      ROOT_ADMIN = aws_cognito_user_group.root_admin_group.name
      ADMIN = aws_cognito_user_group.admin_group.name
      TRAIL_MANAGER = aws_cognito_user_group.trail_manager_group.name
      USER = aws_cognito_user_group.default_user_group.name
    }
  }
}

resource "aws_lambda_function" "change_user_group" {
  function_name = "${var.deploy_env}_change_user_group"
  role          = aws_iam_role.lambda_iam_role.arn
  handler       = "user_management.change_user_group"
  runtime       = "python3.12"
  filename      = "${path.module}/${local.lambda_code_directory}/zips/user_management.zip"

  environment {
    variables = {
      COGNITO_USER_POOL_ID = aws_cognito_user_pool.user_pool.id
      ROOT_ADMIN = aws_cognito_user_group.root_admin_group.name
      ADMIN = aws_cognito_user_group.admin_group.name
      TRAIL_MANAGER = aws_cognito_user_group.trail_manager_group.name
      USER = aws_cognito_user_group.default_user_group.name
    }
  }
}