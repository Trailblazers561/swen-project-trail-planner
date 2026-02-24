resource "aws_cognito_user_pool" "user_pool" {
  name                = "${var.deploy_env}_${var.default_name}_user_pool"
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
}

resource "aws_cognito_user_pool_client" "client" {
  name         = "${var.deploy_env}_${var.default_name}_cognito_client"
  user_pool_id = aws_cognito_user_pool.user_pool.id

  generate_secret              = false
  explicit_auth_flows          = ["ADMIN_NO_SRP_AUTH", "USER_PASSWORD_AUTH"]
  supported_identity_providers = ["COGNITO"]
}

resource "aws_cognito_user" "admin" {
  user_pool_id = aws_cognito_user_pool.user_pool.id
  username     = "${var.admin_username}"
  password     = "${var.admin_password}"
  attributes = {
    email          = "admin@gmail.com"
    email_verified = true
  }
}

# aws trail manager user role
resource "aws_cognito_user_group" "manager" {
  name         = "${var.deploy_env}_${var.default_name}_trailManager"
  user_pool_id = aws_cognito_user_pool.user_pool.id
  description  = "Trail Manager group, managed by Terraform"
  precedence   = 4
}

# aws admin user role
resource "aws_cognito_user_group" "administrator" {
  name         = "${var.deploy_env}_${var.default_name}_administrator"
  user_pool_id = aws_cognito_user_pool.user_pool.id
  description  = "Administator group, managed by Terraform"
  precedence   = 2
}

# aws root admin user role
resource "aws_cognito_user_group" "root_administrator" {
  name         = "${var.deploy_env}_${var.default_name}_rootAdministrator"
  user_pool_id = aws_cognito_user_pool.user_pool.id
  description  = "Root Administator group, managed by Terraform"
  precedence   = 0
}

# add admin user to group
resource "aws_cognito_user_in_group" "root_admin_users" {
  user_pool_id = aws_cognito_user_pool.user_pool.id
  username     = aws_cognito_user.admin.username
  group_name   = aws_cognito_user_group.root_administrator.name
}