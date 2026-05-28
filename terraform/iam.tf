terraform {
  required_providers {
    aws = {
      source  = "hashicorp/aws"
      version = "6.17.0"
    }
  }
}
data "aws_iam_policy_document" "assume_role" {
  statement {
    effect = "Allow"

    principals {
      type        = "Service"
      identifiers = ["lambda.amazonaws.com"]
    }

    actions = ["sts:AssumeRole"]
  }

  statement {
    effect = "Allow"

    principals {
      type        = "Service"
      identifiers = ["apigateway.amazonaws.com"]
    }

    actions = ["sts:AssumeRole"]
  }
}

data "aws_iam_policy_document" "secrets_policy" {
  statement {
    effect = "Allow"

    actions = [
      "secretsmanager:CreateSecret",
      "secretsmanager:UpdateSecret",
      "secretsmanager:GetSecretValue",
      "secretsmanager:DeleteSecret"
    ]

    resources = [
      "arn:aws:secretsmanager:${data.aws_region.current.name}:*:secret:*"
    ]
  }
}

data "aws_iam_policy_document" "ca_policy" {
  statement {
    effect = "Allow"

    principals {
      type        = "Service"
      identifiers = ["ec2.amazonaws.com"]
    }

    actions = ["sts:AssumeRole"]
  }
}

data "aws_iam_policy_document" "ca_secrets_policy" {
  statement {
    effect = "Allow"

    actions = [
      "secretsmanager:CreateSecret",
      "secretsmanager:UpdateSecret",
      "secretsmanager:GetSecretValue",
      "secretsmanager:DeleteSecret"
    ]

    resources = [
      "arn:aws:secretsmanager:${data.aws_region.current.name}:*:secret:cert-auth*"
    ]
  }
}

resource "aws_iam_policy" "secrets_policy" {
  name   = "${var.deploy_env}_secrets_policy"
  policy = data.aws_iam_policy_document.secrets_policy.json
}

#May want to be limited in the future for security concerns
resource "aws_iam_role_policy_attachment" "lambda_dynamodb_full_access" {
  role       = aws_iam_role.lambda_iam_role.name
  policy_arn = "arn:aws:iam::aws:policy/AmazonDynamoDBFullAccess"
}

resource "aws_iam_role_policy_attachment" "lambda_s3_full_access" {
  role       = aws_iam_role.lambda_iam_role.name
  policy_arn = "arn:aws:iam::aws:policy/AmazonS3FullAccess"
}

resource "aws_iam_role_policy_attachment" "lambda_cognito_full_access" {
  role = aws_iam_role.lambda_iam_role.name
  policy_arn = "arn:aws:iam::aws:policy/AmazonCognitoPowerUser"
}

# Allows cloudwatch log access for lambda (local only for cost)
resource "aws_iam_role_policy_attachment" "cloudwatch_logs" {
  count = local.local_run ? 1 : 0
  role = aws_iam_role.lambda_iam_role.name
  policy_arn = "arn:aws:iam::aws:policy/service-role/AWSLambdaBasicExecutionRole"
}

resource "aws_iam_role_policy_attachment" "lambda_secrets_access" {
  role       = aws_iam_role.lambda_iam_role.name
  policy_arn = aws_iam_policy.secrets_policy.arn
}

resource "aws_iam_role_policy_attachment" "lambda_vpc_access" {
  role       = aws_iam_role.lambda_iam_role.name
  policy_arn = "arn:aws:iam::aws:policy/service-role/AWSLambdaVPCAccessExecutionRole"
}

resource "aws_iam_role" "lambda_iam_role" {
  name               = "${var.deploy_env}_lambda_iam_role"
  assume_role_policy = data.aws_iam_policy_document.assume_role.json
}

resource "aws_iam_role" "ca_iam_role" {
  name = "${var.deploy_env}_ca_iam_role"
  assume_role_policy = data.aws_iam_policy_document.ca_policy.json
}

resource "aws_iam_role_policy" "ca_secrets" {
  name = "${var.deploy_env}_ca_secrets_policy"
  role = aws_iam_role.ca_iam_role.id
  policy = data.aws_iam_policy_document.ca_secrets_policy.json
}

resource "aws_iam_instance_profile" "ca_instance_profile" {
  name = "${var.deploy_env}_ca_profile"
  role = aws_iam_role.ca_iam_role.name
}