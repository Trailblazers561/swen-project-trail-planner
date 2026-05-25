locals {
  s3_origin_id = "trailplannerS3Origin"
}

# CloudFront origin access control — lets CloudFront read from a private S3 bucket
# without making the bucket itself public.
resource "aws_cloudfront_origin_access_control" "s3_access" {
  count = var.manage_dns ? 1 : 0

  name                              = "${local.name_prefix}s3_access"
  description                       = "S3 origin access policy"
  origin_access_control_origin_type = "s3"
  signing_behavior                  = "always"
  signing_protocol                  = "sigv4"
}

# CloudFront distribution — the CDN sitting in front of the React app's S3 bucket.
# Aliased to var.dashboard_domain (e.g. adk.trailcount.io), uses the ACM cert we
# created in acm.tf. Implicit dependency on aws_acm_certificate_validation ensures
# the cert is ISSUED before CloudFront tries to use it.
resource "aws_cloudfront_distribution" "s3_distribution" {
  count = var.manage_dns ? 1 : 0

  origin {
    domain_name              = aws_s3_bucket.bucket.bucket_regional_domain_name
    origin_access_control_id = aws_cloudfront_origin_access_control.s3_access[0].id
    origin_id                = local.s3_origin_id
  }

  aliases = [var.dashboard_domain]

  enabled             = true
  is_ipv6_enabled     = true
  comment             = "${local.name_prefix}dashboard"
  default_root_object = "index.html"

  default_cache_behavior {
    allowed_methods  = ["DELETE", "GET", "HEAD", "OPTIONS", "PATCH", "POST", "PUT"]
    cached_methods   = ["GET", "HEAD"]
    target_origin_id = local.s3_origin_id

    forwarded_values {
      query_string = false

      cookies {
        forward = "none"
      }
    }

    viewer_protocol_policy = "redirect-to-https"
    min_ttl                = 0
    default_ttl            = 3600
    max_ttl                = 86400
  }

  ordered_cache_behavior {
    path_pattern     = "/content/immutable/*"
    allowed_methods  = ["GET", "HEAD", "OPTIONS"]
    cached_methods   = ["GET", "HEAD", "OPTIONS"]
    target_origin_id = local.s3_origin_id

    forwarded_values {
      query_string = false
      headers      = ["Origin"]

      cookies {
        forward = "none"
      }
    }

    min_ttl                = 0
    default_ttl            = 86400
    max_ttl                = 31536000
    compress               = true
    viewer_protocol_policy = "redirect-to-https"
  }

  ordered_cache_behavior {
    path_pattern     = "/content/*"
    allowed_methods  = ["GET", "HEAD", "OPTIONS"]
    cached_methods   = ["GET", "HEAD"]
    target_origin_id = local.s3_origin_id

    forwarded_values {
      query_string = false

      cookies {
        forward = "none"
      }
    }

    min_ttl                = 0
    default_ttl            = 3600
    max_ttl                = 86400
    compress               = true
    viewer_protocol_policy = "redirect-to-https"
  }

  # Edge locations: US + EU only (cost optimization).
  price_class = "PriceClass_100"

  # Restrict viewer access to North America.
  restrictions {
    geo_restriction {
      restriction_type = "whitelist"
      locations        = ["US", "CA"]
    }
  }

  # SPA routing: serve index.html for 403s so React Router can handle deep links.
  custom_error_response {
    error_code            = 403
    response_page_path    = "/index.html"
    response_code         = 200
    error_caching_min_ttl = 300
  }

  tags = {
    Name   = "${local.name_prefix}dashboard"
    Tenant = var.tenant
    Env    = var.env
  }

  viewer_certificate {
    acm_certificate_arn      = aws_acm_certificate_validation.dashboard[0].certificate_arn
    ssl_support_method       = "sni-only"
    minimum_protocol_version = "TLSv1.2_2021"
  }

  depends_on = [aws_s3_bucket.bucket, null_resource.deploy_react_app]
}

# Bucket policy that lets only this CloudFront distribution read the bucket.
# Replaces the public-read policy in s3.tf for manage_dns workspaces.
resource "aws_s3_bucket_policy" "cloudfront_s3_bucket_policy" {
  count = var.manage_dns ? 1 : 0

  bucket = aws_s3_bucket.bucket.id
  policy = jsonencode({
    Version = "2008-10-17"
    Id      = "PolicyForCloudFrontPrivateContent"
    Statement = [
      {
        Sid    = "AllowCloudFrontServicePrincipal"
        Effect = "Allow"
        Principal = {
          Service = "cloudfront.amazonaws.com"
        }
        Action   = "s3:GetObject"
        Resource = "${aws_s3_bucket.bucket.arn}/*"
        Condition = {
          StringEquals = {
            "AWS:SourceArn" = aws_cloudfront_distribution.s3_distribution[0].arn
          }
        }
      }
    ]
  })

  depends_on = [aws_cloudfront_distribution.s3_distribution]
}

output "website_url" {
  value = var.manage_dns ? "https://${var.dashboard_domain}" : "http://${aws_s3_bucket_website_configuration.website[0].website_endpoint}"
}
