resource "aws_s3_bucket" "bucket" {
  bucket = var.has_domain ? "${var.deploy_env}.${var.domain}" : "${var.deploy_env}-${var.bucket_name}-${random_integer.random_suffix.result}"

  tags = {
    Name = "${var.deploy_env}-${var.bucket_name}"
  }

  force_destroy = true
}

resource "aws_s3_bucket_public_access_block" "public_access" {
  count = var.has_cdn ? 0 : 1

  bucket = aws_s3_bucket.bucket.id

  block_public_acls       = false
  block_public_policy     = false
  ignore_public_acls      = false
  restrict_public_buckets = false
}

output "react_bucket_name" {
  value = aws_s3_bucket.bucket.bucket
}

resource "aws_s3_bucket_policy" "public_read" {
  count = var.has_cdn ? 0 : 1

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

  depends_on = [aws_s3_bucket_public_access_block.public_access]
}

resource "aws_s3_bucket_website_configuration" "website" {
  count = var.has_cdn ? 0 : 1

  bucket = aws_s3_bucket.bucket.id

  index_document {
    suffix = "index.html"
  }

  error_document {
    key = "index.html"
  }

  depends_on = [aws_s3_bucket_public_access_block.public_access]
}

resource "aws_s3_bucket_ownership_controls" "bucket_ownership" {
  bucket = aws_s3_bucket.bucket.id
  rule {
    object_ownership = "BucketOwnerPreferred"
  }
}

resource "aws_s3_bucket_acl" "acl" {
  depends_on = [aws_s3_bucket_ownership_controls.bucket_ownership, aws_s3_bucket_public_access_block.public_access]

  bucket = aws_s3_bucket.bucket.id
  acl    = var.has_cdn ? var.bucket_acl : "public-read"
}

#Injects user pool configuration into environment
resource "local_sensitive_file" "user_pool_config" {
  content    = <<EOF
{
    "region": "us-east-1",
    "userPoolId": "${aws_cognito_user_pool.user_pool.id}",
    "clientId": "${aws_cognito_user_pool_client.client.id}"
}
EOF
  filename   = "${path.module}/${local.react_app_directory}/src/cognito/config.json"
  depends_on = [aws_cognito_user_pool.user_pool, aws_cognito_user_pool_client.client]
}

resource "null_resource" "deploy_react_app" {
  count = local.local_run ? 1 : 0
  provisioner "local-exec" {
    command = "cd ${local.react_app_directory} && npm install && npm run build && aws s3 sync ./dist s3://${aws_s3_bucket.bucket.bucket} --delete"
  }

  depends_on = [aws_s3_bucket.bucket, local_sensitive_file.user_pool_config, local_sensitive_file.frontend_env]
}

resource "aws_s3_bucket" "csv_bucket" {
  bucket = "${var.deploy_env}-csv-bucket-${random_integer.random_suffix.result}"

  tags = {
    Name = "${var.deploy_env}-csv-bucket"
  }

  force_destroy = true
}

resource "aws_s3_bucket" "truststore_bucket" {
  bucket = "${var.deploy_env}-truststore-bucket-${random_integer.random_suffix.result}"

  tags = {
    Name = "${var.deploy_env}-truststore-bucket"
  }

  force_destroy = true
}