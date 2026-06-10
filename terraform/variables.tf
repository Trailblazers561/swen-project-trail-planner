variable "deploy_env" {
  type = string
  default = "local"
}

locals {
  local_run = var.deploy_env == "local"
  test_run = var.deploy_env == "test"
  react_app_directory = local.local_run ? "../swen-project-react-app" : "./swen-project-react-app"
  lambda_code_directory = local.local_run ? "../lambdas" : "./lambdas"
  test_directory = local.local_run ? "../tests" : "./tests"
  sample_data_directory = local.local_run ? "../sample_data" : "./sample_data"
}

// This can be changed later to not be defined here, but for now it's not less secure than before
locals {
  password = local.test_run ? "testPassword123!" : "password" # Sometimes google tells you your password has been found, this avoids that issue when testing
  users = {
    root_admin = { email = "root_admin@gmail.com", password = local.password, groups=["root_admin", "admin", "trail_manager", "user"] }
    admin = { email = "admin@gmail.com", password = local.password, groups=["admin", "trail_manager", "user"] }
    trail_manager = { email = "trail_manager@gmail.com", password = local.password, groups=["trail_manager", "user"] }
    user = { email = "user@gmail.com", password = local.password, groups=["user"] }
  }
}

locals {
  use_domain = !local.local_run && !local.test_run
  domain = "trailcount.io"
  cloudfront_sub_domain = "${var.deploy_env}"
  api_sub_domain = "public-api-${var.deploy_env}"
  verification_email = local.local_run ? var.local_user_email : "TrailCount@auth.${local.domain}"
}

// Will get populated from github actions and stored in the repo, not populated in a local run
variable "acm_certificate_arn" {
  type        = string
  default     = "arn:"
  description = "Domain certificate arn"
}

// Will get populated from github actions and stored in the repo, should be overriden for a local run too
variable "ses_identity_arn" {
  type        = string
  default     = "arn:"
  description = "SES identity arn"
}

variable "local_user_email" {
  type = string
  default = "email@g.rit.edu"
}

variable "bucket_name" {
  type    = string
  default = "trailcount-bucket"
}

# Set to false to disable auth
variable "authorization_enabled" {
  type = bool
  default = true
}

locals {
  gateway_method_authorization = var.authorization_enabled ? "CUSTOM" : "NONE"
  gateway_authorizer_type = var.authorization_enabled ? "TOKEN" : "NONE"
}

resource "random_integer" "random_suffix" {
  min = 10000000
  max = 99999999
}