# Device API key generation for tenant-scoped workspaces.
#
# Legacy workspaces (default, tst) set var.device_api_key in their tfvars files
# and that value is used directly.
#
# New tenant-scoped workspaces (manage_dns=true) get an auto-generated 32-char
# random key. After `terraform apply`, retrieve it with:
#   AWS_PROFILE=trail-admin terraform output -raw device_api_key
# Then paste into firmware Core/Inc/secrets.h and rebuild + flash.

resource "random_password" "device_api_key" {
  count   = var.manage_dns ? 1 : 0
  length  = 32
  special = false
}

resource "random_password" "admin_password" {
  count = var.admin_password == null ? 1 : 0
  length = 8
  special = false
}

locals {
  effective_device_api_key = var.manage_dns ? random_password.device_api_key[0].result : var.device_api_key
  effective_admin_password = var.admin_password != null ? var.admin_password : random_password.admin_password[0]
}
