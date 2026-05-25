# ACM certificates for tenant-scoped domains.
# Both certs are issued in us-east-1 (CloudFront *requires* us-east-1 certs).
# All resources gated by var.manage_dns so legacy workspaces are inert.

# Dashboard cert — covers e.g. adk.trailcount.io. Used by CloudFront.
resource "aws_acm_certificate" "dashboard" {
  count             = var.manage_dns ? 1 : 0
  domain_name       = var.dashboard_domain
  validation_method = "DNS"

  lifecycle {
    create_before_destroy = true
  }

  tags = {
    Name   = "${local.name_prefix}dashboard-cert"
    Tenant = var.tenant
    Env    = var.env
  }
}

# API cert — covers e.g. api.adk.trailcount.io. Used by API Gateway custom domain.
resource "aws_acm_certificate" "api" {
  count             = var.manage_dns ? 1 : 0
  domain_name       = var.api_domain
  validation_method = "DNS"

  lifecycle {
    create_before_destroy = true
  }

  tags = {
    Name   = "${local.name_prefix}api-cert"
    Tenant = var.tenant
    Env    = var.env
  }
}

# Validation gates. terraform apply pauses on these resources until ACM
# confirms cert issuance — which only happens once the validation CNAMEs
# appear in DNS (Squarespace, in our case). To see what CNAMEs to add,
# run `terraform output` (see outputs.tf added in A2.3e) in another terminal
# while apply is paused.
resource "aws_acm_certificate_validation" "dashboard" {
  count           = var.manage_dns ? 1 : 0
  certificate_arn = aws_acm_certificate.dashboard[0].arn
}

resource "aws_acm_certificate_validation" "api" {
  count           = var.manage_dns ? 1 : 0
  certificate_arn = aws_acm_certificate.api[0].arn
}
