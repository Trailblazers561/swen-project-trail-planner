resource "aws_cognito_user_pool" "user_pool" {
  name                = "${var.deploy_env}_trailplanner_user_pool"
  deletion_protection = "INACTIVE"

  username_attributes      = ["email"]
  auto_verified_attributes = ["email"]

  password_policy {
    minimum_length    = 6
    require_lowercase = false
    require_uppercase = false
    require_numbers   = false
    require_symbols   = false
  }

  lambda_config {
    post_confirmation  = aws_lambda_function.confirm_user.arn
  }

  verification_message_template {
    default_email_option = "CONFIRM_WITH_LINK"
  }
}

resource "aws_cognito_user_pool_domain" "user_pool_domain" {
  domain       = "${var.deploy_env}-trailplanner-user-confirmation"
  user_pool_id = aws_cognito_user_pool.user_pool.id
}

resource "aws_cognito_user_pool_client" "client" {
  name         = "${var.deploy_env}_trailplanner_cognito_client"
  user_pool_id = aws_cognito_user_pool.user_pool.id

  generate_secret              = false
  explicit_auth_flows          = ["ADMIN_NO_SRP_AUTH", "USER_PASSWORD_AUTH"]
  supported_identity_providers = ["COGNITO"]
  refresh_token_rotation {
    feature = "ENABLED"
    retry_grace_period_seconds = 0
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
  username = each.value.username
  password = each.value.password

  attributes = {
    email = each.value.email
    email_verified = true
  }
}

locals {
  users_in_groups = {
    for pair in flatten([for _, user in local.users : [for group in user.groups : {username = user.username, group = group}]]) :
    "${pair.username}|${pair.group}" => pair
  }
}

# Assign Predefined Users To Groups
resource "aws_cognito_user_in_group" "assign_users" {
  for_each = local.users_in_groups

  user_pool_id = aws_cognito_user_pool.user_pool.id
  username     = each.value.username
  group_name   = "${each.value.group}"

  depends_on = [aws_cognito_user.users]
}