variable "default_name" {
  type    = string
  default = "trailplanner"
}

variable "deploy_env" {
  type = string
  default = "local"
}

variable "local_run" {
  type = bool
  default = true
}

locals {
  react_app_directory = var.local_run ? "../swen-project-react-app" : "./swen-project-react-app"
  lambda_code_directory = var.local_run ? "../lambdas" : "./lambdas"
  test_directory = var.local_run ? "../tests" : "./tests"
}

// This can be changed later to not be defined here, but for now it's not less secure than before
variable "admin_username" {
  type = string
  default = "admin@gmail.com"
}

variable "admin_password" {
  type = string
  default = "password"
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



variable "authorization_type" {
  type = string
  #Set to "NONE" to disable auth
  default = "COGNITO_USER_POOLS"
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