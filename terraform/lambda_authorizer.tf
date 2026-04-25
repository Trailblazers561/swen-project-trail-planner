# Lambda Authorizer Lambda Function
resource "aws_lambda_function" "lambda_authorizer" {
  function_name = "${var.deploy_env}_trailplanner_api_authorizer"
  role          = aws_iam_role.lambda_authorizer_role.arn
  handler       = "lambda_authorizer.handler"
  runtime       = "python3.12"
  filename      = "${path.module}/${local.lambda_code_directory}/zips/lambda_authorizer.zip"
  code_sha256 = data.archive_file.lambda_authorizer_zip.output_base64sha256
  layers           = [aws_lambda_layer_version.authorizer_layer.arn]

  environment {
    variables = {
      COGNITO_USER_POOL_ID = aws_cognito_user_pool.user_pool.id
      COGNITO_APP_CLIENT_ID = aws_cognito_user_pool_client.client.id
      ROOT_ADMIN = aws_cognito_user_group.root_admin_group.name
      ADMIN = aws_cognito_user_group.admin_group.name
      TRAIL_MANAGER = aws_cognito_user_group.trail_manager_group.name
      USER = aws_cognito_user_group.default_user_group.name
    }
  }
}

resource "null_resource" "authorizer_pip_install" {
  count = local.local_run ? 1 : 0

  triggers = {
    shell_hash = filesha256("${path.module}/${local.lambda_code_directory}/lambda_authorizer/requirements.txt")
  }

  provisioner "local-exec" {
    command = "python -m pip install --no-compile --no-binary :all: -r ${path.module}/${local.lambda_code_directory}/lambda_authorizer/requirements.txt -t ${path.module}/${local.lambda_code_directory}/layers/auth_reqs/python"
  }
}

data "archive_file" "authorizer_layer" {
  type        = "zip"
  source_dir  = "${path.module}/${local.lambda_code_directory}/layers/auth_reqs"
  output_path = "${path.module}/${local.lambda_code_directory}/zips/auth_reqs_layer.zip"
  depends_on  = [null_resource.authorizer_pip_install]
}

resource "aws_lambda_layer_version" "authorizer_layer" {
  layer_name          = "${var.deploy_env}-trailplanner-authorizer-layer"
  filename            = data.archive_file.authorizer_layer.output_path
  source_code_hash    = data.archive_file.authorizer_layer.output_base64sha256
  compatible_runtimes = ["python3.12"]
}

data "archive_file" "lambda_authorizer_zip" {
  type        = "zip"
  source_file  = "${path.module}/${local.lambda_code_directory}/lambda_authorizer/lambda_authorizer.py"
  output_path = "${path.module}/${local.lambda_code_directory}/zips/lambda_authorizer.zip"
}

# Lambda Authorizer Role
resource "aws_iam_role" "lambda_authorizer_role" {
  name               = "${var.deploy_env}_trailplanner_lambda_authorizer_role"
  assume_role_policy = data.aws_iam_policy_document.assume_role.json
}

# Allows cloudwatch log access for lambda (local only for cost)
resource "aws_iam_role_policy_attachment" "authorizer_cloudwatch_logs" {
  count = local.local_run ? 1 : 0
  role = aws_iam_role.lambda_authorizer_role.name
  policy_arn = "arn:aws:iam::aws:policy/service-role/AWSLambdaBasicExecutionRole"
}