resource "aws_s3_bucket" "bucket" {
  bucket = "${var.bucket_name}-${random_integer.random_suffix.result}"
  
  tags = {
    Name = var.bucket_name
  }

  force_destroy = true
}

resource "aws_s3_bucket_public_access_block" "public_access" {
  count = var.fast_boot ? 1 : 0

  bucket = aws_s3_bucket.bucket.id

  block_public_acls       = false
  block_public_policy     = false
  ignore_public_acls      = false
  restrict_public_buckets = false
}

resource "aws_s3_bucket_policy" "public_read" {
  count = var.fast_boot ? 1 : 0

  bucket = aws_s3_bucket.bucket.id
  policy = jsonencode({
    Version = "2012-10-17",
    Statement = [
      {
        Effect    = "Allow",
        Principal = "*",
        Action    = "s3:GetObject",
        Resource  = "${aws_s3_bucket.bucket.arn}/*"
      }
    ]
  })

  depends_on = [ aws_s3_bucket_public_access_block.public_access ]
}

resource "aws_s3_bucket_website_configuration" "website" {
  count = var.fast_boot ? 1 : 0

  bucket = aws_s3_bucket.bucket.id

  index_document {
    suffix = "index.html"
  }

  error_document {
    key = "index.html"
  }

  depends_on = [ aws_s3_bucket_public_access_block.public_access ]
}

resource "aws_s3_bucket_ownership_controls" "bucket_ownership" {
  bucket = aws_s3_bucket.bucket.id
  rule {
    object_ownership = "BucketOwnerPreferred"
  }
}

resource "aws_s3_bucket_acl" "acl" {
  depends_on = [ aws_s3_bucket_ownership_controls.bucket_ownership, aws_s3_bucket_public_access_block.public_access ]

  bucket = aws_s3_bucket.bucket.id
  acl    = var.fast_boot ?  "public-read" : var.bucket_acl
}

#Injects user pool configuration into environment
resource "local_sensitive_file" "user_pool_config" {
  content = <<EOF
{
    "region": "us-east-1",
    "userPoolId": "${aws_cognito_user_pool.user_pool.id}",
    "clientId": "${aws_cognito_user_pool_client.client.id}"
}
EOF
  filename = "${path.module}/${var.react_app_directory}/src/cognito/config.json"
  depends_on = [ aws_cognito_user_pool.user_pool, aws_cognito_user_pool_client.client]
}

resource "null_resource" "deploy_react_app" {
  provisioner "local-exec" {
    command = "cd ${var.react_app_directory} && npm install && npm run build && aws s3 sync ./dist s3://${aws_s3_bucket.bucket.bucket} --delete"
  }

  depends_on = [aws_s3_bucket.bucket, local_sensitive_file.user_pool_config, local_sensitive_file.production_env]
}
