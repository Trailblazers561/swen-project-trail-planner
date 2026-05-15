# API Gateway custom domain — maps var.api_domain (e.g. api.adk.trailcount.io)
# onto the existing REST API stage. Gated by var.manage_dns.
#
# After apply, you'll add a CNAME in Squarespace pointing var.api_domain at
# aws_api_gateway_domain_name.api.regional_domain_name (see outputs in A2.3e).

resource "aws_api_gateway_domain_name" "api" {
  count                    = var.manage_dns ? 1 : 0
  domain_name              = var.api_domain
  regional_certificate_arn = aws_acm_certificate_validation.api[0].certificate_arn

  # REGIONAL = direct hit to API Gateway in us-east-1.
  # EDGE = add CloudFront caching in front (not needed for our use case).
  endpoint_configuration {
    types = ["REGIONAL"]
  }

  tags = {
    Name   = "${local.name_prefix}api-domain"
    Tenant = var.tenant
    Env    = var.env
  }
}

# Maps the custom domain at root path "" to the existing API Gateway stage,
# so api.adk.trailcount.io/devices reaches the same handler as the default URL.
resource "aws_api_gateway_base_path_mapping" "api" {
  count       = var.manage_dns ? 1 : 0
  api_id      = aws_api_gateway_rest_api.api.id
  stage_name  = aws_api_gateway_stage.api_stage.stage_name
  domain_name = aws_api_gateway_domain_name.api[0].domain_name
}
