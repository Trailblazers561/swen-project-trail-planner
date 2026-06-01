resource "aws_cognito_user_pool" "user_pool" {
  name                = "${var.deploy_env}_traillcount_user_pool"
  deletion_protection = "INACTIVE"

  alias_attributes = ["email"]
  auto_verified_attributes = ["email"]

  password_policy {
    minimum_length    = 6
    require_lowercase = false
    require_uppercase = false
    require_numbers   = false
    require_symbols   = false
  }

  lambda_config {
    pre_sign_up = aws_lambda_function.cognito_config_lambdas["pre_sign_up"].arn
    post_confirmation = aws_lambda_function.cognito_config_lambdas["post_confirmation"].arn
    custom_message = aws_lambda_function.cognito_config_lambdas["custom_message"].arn
  }

  email_configuration {
    email_sending_account = "DEVELOPER"
    from_email_address = local.verification_email
    source_arn = var.ses_identity_arn
  }
}

resource "aws_cognito_user_pool_domain" "user_pool_domain" {
  domain       = "${var.deploy_env}-traillcount-user-confirmation"
  user_pool_id = aws_cognito_user_pool.user_pool.id
}

resource "aws_cognito_user_pool_client" "client" {
  name         = "${var.deploy_env}_traillcount_cognito_client"
  user_pool_id = aws_cognito_user_pool.user_pool.id

  generate_secret              = false
  explicit_auth_flows          = ["ADMIN_NO_SRP_AUTH", "USER_PASSWORD_AUTH"]
  supported_identity_providers = ["COGNITO"]

  refresh_token_rotation {
    feature = "ENABLED"
    retry_grace_period_seconds = 10
  }
}

resource "aws_cognito_user_group" "root_admin_group" {
  name = "root_admin"
  user_pool_id = aws_cognito_user_pool.user_pool.id
  description  = "Root Admin group, managed by Terraform"
  precedence   = 0
}

resource "aws_cognito_user_group" "admin_group" {
  name         = "admin"
  user_pool_id = aws_cognito_user_pool.user_pool.id
  description  = "Admin group, managed by Terraform"
  precedence   = 2
}

resource "aws_cognito_user_group" "trail_manager_group" {
  name         = "trail_manager"
  user_pool_id = aws_cognito_user_pool.user_pool.id
  description  = "Trail Manager group, managed by Terraform"
  precedence   = 4
}

resource "aws_cognito_user_group" "default_user_group" {
  name         = "user"
  user_pool_id = aws_cognito_user_pool.user_pool.id
  description  = "Default User group, managed by Terraform"
  precedence   = 6
}

# Create Predefined Users
resource "aws_cognito_user" "users" {
  for_each = local.users

  user_pool_id = aws_cognito_user_pool.user_pool.id
  username = each.key
  password = each.value.password

  attributes = {
    email = each.value.email
    email_verified = true
  }
}

locals {
  users_in_groups = {
    for username_group in flatten([for username, user in local.users : [for group in user.groups : {username = username, group = group}]]) :
    "${username_group.username}|${username_group.group}" => username_group
  }
}

# Assign Predefined Users To Groups
resource "aws_cognito_user_in_group" "assign_users" {
  for_each = local.users_in_groups

  user_pool_id = aws_cognito_user_pool.user_pool.id
  username     = each.value.username
  group_name   = each.value.group

  depends_on = [aws_cognito_user.users]
}