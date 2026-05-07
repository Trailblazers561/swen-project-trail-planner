variable "default_name" {
  type    = string
  default = "trailplanner"
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

variable "react_app_directory" {
  type    = string
  default = "../swen-project-react-app"
}

variable "authorization_type" {
  type = string
  #Set to "NONE" to disable auth
  default = "COGNITO_USER_POOLS"
}

# ONLY USE FOR TESTING. Removes CDN optimizations and exposes all files in the s3 to the public with read permissions.
variable "has_cdn" {
  type    = bool
  default = false
}

variable "device_api_key" {
  type      = string
  sensitive = true
  default   = null
  description = "API key value for the device endpoint. Null = AWS auto-generates (use for staging)."
}

variable "env" {
  type        = string
  default     = ""
  description = "Environment prefix for resource names (e.g. 'tst'). Empty string = no prefix (prod)."
}

locals {
  name_prefix = var.env != "" ? "${var.env}-" : ""
}

resource "random_integer" "random_suffix" {
  min = 10000000
  max = 99999999
}