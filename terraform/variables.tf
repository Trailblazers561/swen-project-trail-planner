variable "default_name" {
  type = string
  default = "trailplanner"
}

variable "domain" {
  type = string
  default = "no-lan.com"
}

variable "has_domain" {
  type = bool
  default = false
}

variable "bucket_name" {
  type = string
  default = "trailplanner-bucket"
}

variable "bucket_acl" {
  type        = string
  default     = "private"
  description = "Bucket ACL (Access Control Listing)"
}

variable "react_app_directory" {
  type        = string
  default     = "../swen-project-react-app"
}

variable "authorization_type" {
  type        = string
  #Set to "NONE" to disable auth
  default     = "COGNITO_USER_POOLS"
}

# ONLY USE FOR TESTING. Removes CDN optimizations and exposes all files in the s3 to the public with read permissions.
variable "has_cdn" {
  type = bool
  default = true
}

resource "random_integer" "random_suffix" {
  min = 10000000
  max = 99999999
}