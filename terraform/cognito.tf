resource "aws_cognito_user_pool" "user_pool" {
  name = "${var.default_name}_user_pool"
  deletion_protection = "INACTIVE"

  username_attributes = ["email"]
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

  generate_secret = false
  explicit_auth_flows = ["ADMIN_NO_SRP_AUTH", "USER_PASSWORD_AUTH"]
  supported_identity_providers = ["COGNITO"]
}