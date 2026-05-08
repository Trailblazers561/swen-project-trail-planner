resource "aws_cognito_user_pool" "user_pool" {
  name                = "${var.default_name}_user_pool"
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
  name         = "${var.default_name}_cognito_client"
  user_pool_id = aws_cognito_user_pool.user_pool.id

  generate_secret              = false
  explicit_auth_flows          = ["ADMIN_NO_SRP_AUTH", "USER_PASSWORD_AUTH"]
  supported_identity_providers = ["COGNITO"]

  access_token_validity = 8
  id_token_validity     = 8
  token_validity_units {
    access_token = "hours"
    id_token     = "hours"
  }
}

resource "aws_cognito_user" "admin" {
  user_pool_id = aws_cognito_user_pool.user_pool.id
  username     = "admin@gmail.com"
  password     = "password"
  attributes = {
    email          = "admin@gmail.com"
    email_verified = true
  }
}