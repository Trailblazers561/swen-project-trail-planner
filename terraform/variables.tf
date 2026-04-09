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
}

// This can be changed later to not be defined here, but for now it's not less secure than before
variable "users" {
  type = map(object({
    username = string
    password = string
    email = string
  }))
  default = {
    root_admin = { username = "root_admin@gmail.com",    password = "password", email = "root_admin@gmail.com" }
    admin = { username = "admin@gmail.com",    password = "password", email = "admin@gmail.com" }
    trail_manager = { username = "trail_manager@gmail.com", password = "password", email = "trail_manager@gmail.com" }
    user = { username = "user@gmail.com",   password = "password",  email = "user@gmail.com" }
  }
}

locals {
  use_domain = !local.local_run && !local.test_run
  domain = "adirondackwilderness.org"
  sub_domain = "trailblazers-${var.deploy_env}"
}

// Will get populated from github actions and stored in the repo, not populated in a local run
variable "acm_certificate_arn" {
  type        = string
  default     = "arn:"
  description = "Domain certificate arn"
}

variable "bucket_name" {
  type    = string
  default = "trailplanner-bucket"
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