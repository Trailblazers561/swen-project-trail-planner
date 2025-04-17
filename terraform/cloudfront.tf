locals {
  s3_origin_id = var.has_domain ? var.domain : "trailplannerS3Origin"
}

resource "aws_cloudfront_origin_access_control" "s3_access" {
  count = var.has_cdn ? 1 : 0

  name                              = "s3_access"
  description                       = "s3 origin access policy"
  origin_access_control_origin_type = "s3"
  signing_behavior                  = "always"
  signing_protocol                  = "sigv4"
}

resource "aws_cloudfront_distribution" "s3_distribution" {
  count = var.has_cdn ? 1 : 0

  origin {
    domain_name              = var.has_domain ? "${var.domain}.s3.amazonaws.com" : aws_s3_bucket.bucket.bucket_regional_domain_name
    origin_access_control_id = aws_cloudfront_origin_access_control.s3_access[0].id
    origin_id                = local.s3_origin_id
  }

  aliases = var.has_domain ? [var.domain] : []

  enabled             = true
  is_ipv6_enabled     = true
  comment             = "Some comment"
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
    error_code           = 403
    response_page_path   = "/index.html"
    response_code        = 200
    error_caching_min_ttl = 300
  }

  tags = {
    Environment = "production"
  }

  viewer_certificate {
    cloudfront_default_certificate = true
  }

  depends_on = [ aws_s3_bucket.bucket, null_resource.deploy_react_app ]
}

#Allows cloudfront access to react app bucket. Otherwise cloudfront will not have access to content and therefore be unable to deliver site.
resource "aws_s3_bucket_policy" "cloudfront_s3_bucket_policy" {
  count = var.has_cdn ? 1 : 0

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

  depends_on = [ aws_cloudfront_distribution.s3_distribution ]
}

output "website_url" {
  value = var.has_cdn ? "http://${aws_cloudfront_distribution.s3_distribution[0].domain_name}" : "http://${aws_s3_bucket_website_configuration.website[0].website_endpoint}"
}

