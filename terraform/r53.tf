resource "aws_route53_zone" "primary" {
  count = (var.has_cdn && var.has_domain) ? 1 : 0

  name = var.domain
}

resource "aws_route53_record" "www" {
  count = (var.has_cdn && var.has_domain) ? 1 : 0

  zone_id = aws_route53_zone.primary[0].zone_id
  name    = var.domain
  type    = "A"

  alias {
    name                   = aws_cloudfront_distribution.s3_distribution[0].domain_name
    zone_id                = aws_cloudfront_distribution.s3_distribution[0].hosted_zone_id
    evaluate_target_health = false
  }

  depends_on = [ aws_cloudfront_distribution.s3_distribution, aws_route53_zone.primary ]
}