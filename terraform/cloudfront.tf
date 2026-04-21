locals {
  s3_origin_id = local.use_domain ? "${local.sub_domain}.${local.domain}" : "trailplannerS3Origin"
  full_domain  = local.use_domain ? "${local.sub_domain}.${local.domain}" : ""
}

resource "aws_cloudfront_origin_access_control" "s3_access" {
  name                              = "${var.deploy_env}_s3_access"
  description                       = "s3 origin access policy"
  origin_access_control_origin_type = "s3"
  signing_behavior                  = "always"
  signing_protocol                  = "sigv4"
}

resource "aws_cloudfront_distribution" "s3_distribution" {
  origin {
    domain_name              = aws_s3_bucket.bucket.bucket_regional_domain_name
    origin_access_control_id = aws_cloudfront_origin_access_control.s3_access.id
    origin_id                = local.s3_origin_id
  }

  aliases = local.use_domain ? [local.full_domain] : []

  enabled             = true
  is_ipv6_enabled     = true
  comment             = "${var.deploy_env} distribution"
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

  # Cache behavior with precedence 0
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

  # Cache behavior with precedence 1
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

  #Only use edge locations in US and EU
  price_class = "PriceClass_100"

  #Restricts countries access to only North American countries
  restrictions {
    geo_restriction {
      restriction_type = "whitelist"
      locations        = ["US", "CA"]
    }
  }

  #Ensures cloudfront is always routed to our App.jsx router
  custom_error_response {
    error_code            = 403
    response_page_path    = "/index.html"
    response_code         = 200
    error_caching_min_ttl = 300
  }

  tags = {
    Environment = "${var.deploy_env}"
  }

  #Sets up domain cert uses default cloudfront cert otherwise
  viewer_certificate {
    acm_certificate_arn            = local.use_domain ? var.acm_certificate_arn : null
    ssl_support_method             = local.use_domain ? "sni-only" : null
    minimum_protocol_version       = local.use_domain ? "TLSv1.2_2021" : null
    cloudfront_default_certificate = local.use_domain ? false : true
  }

  depends_on = [aws_s3_bucket.bucket, null_resource.deploy_react_app]
}

#Allows cloudfront access to react app bucket. Otherwise cloudfront will not have access to content and therefore be unable to deliver site.
resource "aws_s3_bucket_policy" "cloudfront_s3_bucket_policy" {
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
            "AWS:SourceArn" = aws_cloudfront_distribution.s3_distribution.arn
          }
        }
      }
    ]
  })

  depends_on = [aws_cloudfront_distribution.s3_distribution]
}

output "website_url" {
  value = "https://${local.use_domain ? local.full_domain : aws_cloudfront_distribution.s3_distribution.domain_name}"
}

output "distribution_id" {
  value = "${aws_cloudfront_distribution.s3_distribution.id}"
}
