# Outputs for the two-wave Squarespace DNS workflow during first apply.
#
# Wave 1 (cert validation): while terraform apply is paused on
#   aws_acm_certificate_validation, run `terraform output -json` in a separate
#   terminal. Take dashboard_cert_validation_records and api_cert_validation_records
#   and add the CNAMEs to Squarespace. ACM polls DNS, validates, apply resumes.
#
# Wave 2 (traffic routing): after apply completes, add the actual user-facing
#   CNAMEs in Squarespace:
#     var.dashboard_domain  CNAME ->  dashboard_cname_target
#     var.api_domain        CNAME ->  api_cname_target

output "dashboard_cert_validation_records" {
  description = "DNS CNAMEs to add to Squarespace so ACM can validate the dashboard cert"
  value = var.manage_dns ? [
    for o in aws_acm_certificate.dashboard[0].domain_validation_options : {
      name  = o.resource_record_name
      type  = o.resource_record_type
      value = o.resource_record_value
    }
  ] : []
}

output "api_cert_validation_records" {
  description = "DNS CNAMEs to add to Squarespace so ACM can validate the API cert"
  value = var.manage_dns ? [
    for o in aws_acm_certificate.api[0].domain_validation_options : {
      name  = o.resource_record_name
      type  = o.resource_record_type
      value = o.resource_record_value
    }
  ] : []
}

output "dashboard_cname_target" {
  description = "Point a CNAME at this from var.dashboard_domain in Squarespace"
  value       = var.manage_dns ? aws_cloudfront_distribution.s3_distribution[0].domain_name : null
}

output "api_cname_target" {
  description = "Point a CNAME at this from var.api_domain in Squarespace"
  value       = var.manage_dns ? aws_api_gateway_domain_name.api[0].regional_domain_name : null
}
