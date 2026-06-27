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

variable "admin_password" {
  type = string
  sensitive = true
  default = null
  description = "The password for the admin account to use."
}

variable "env" {
  type        = string
  default     = ""
  description = "Environment within a tenant (e.g. 'prod', 'test'). Legacy workspaces use '' (default) or 'tst' (legacy staging)."
}

variable "tenant" {
  type        = string
  default     = ""
  description = "Tenant name (e.g. 'adk', 'demo'). Empty = legacy workspaces (default and tst). New tenant-scoped workspaces set this to enable the tc-<tenant>-<env>- naming pattern."
}

variable "manage_dns" {
  type        = bool
  default     = false
  description = "When true, Terraform creates ACM certs + CloudFront with custom domain + API Gateway custom domain. New tenant-scoped workspaces set this true. Legacy workspaces keep it false (DNS/certs managed manually outside Terraform if at all)."
}

variable "dashboard_domain" {
  type        = string
  default     = ""
  description = "Full FQDN for the dashboard (e.g. 'adk.trailcount.io', 'test.adk.trailcount.io'). Used only when manage_dns = true."
}

variable "api_domain" {
  type        = string
  default     = ""
  description = "Full FQDN for the API (e.g. 'api.adk.trailcount.io', 'api.test.adk.trailcount.io'). Used only when manage_dns = true."
}

locals {
  # Resource name prefix. Three cases:
  #   tenant-scoped (tenant='adk', env='test')  -> 'tc-adk-test-'
  #   legacy staging  (tenant='',   env='tst')  -> 'tst-'         (preserves existing behavior)
  #   legacy prod     (tenant='',   env='')     -> ''             (preserves existing behavior)
  name_prefix = var.tenant != "" ? "tc-${var.tenant}-${var.env}-" : (var.env != "" ? "${var.env}-" : "")
}

resource "random_integer" "random_suffix" {
  min = 10000000
  max = 99999999
}