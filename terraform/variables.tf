variable "deploy_env" {
  type = string
  default = "local"
}

locals {
  local_run = var.deploy_env == "local"
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

#root domain
variable "domain" {
  type    = string
  default = "example.com"
}

#sub domain
variable "sub" {
  type    = string
  default = "adiron"
}

variable "has_domain" {
  type    = bool
  default = false
}

#If has domain is true this needs to have a value
variable "acm_certificate_arn" {
  type        = string
  default     = "arn:"
  description = "Domain certificate arn"
}

variable "bucket_name" {
  type    = string
  default = "trailplanner-bucket"
}

variable "bucket_acl" {
  type        = string
  default     = "private"
  description = "Bucket ACL (Access Control Listing)"
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

# ONLY USE FOR TESTING. Removes CDN optimizations and exposes all files in the s3 to the public with read permissions.
variable "has_cdn" {
  type    = bool
  default = true
}

resource "random_integer" "random_suffix" {
  min = 10000000
  max = 99999999
}

variable "ssh_key_name" {
  type = string
  description = "key pair for ssh to the certificate authority on our ec2 instance"
}