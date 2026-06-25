resource "aws_s3_bucket" "react_bucket" {
  bucket = local.use_domain ? "${local.cloudfront_sub_domain}.${local.domain}" : "${var.deploy_env}-trailcount-react-bucket-${random_integer.random_suffix.result}"

  tags = {
    Name = "${var.deploy_env}-trailcount-react-bucket"
  }

  force_destroy = true
}

output "react_bucket_name" {
  value = aws_s3_bucket.react_bucket.bucket
}

resource "aws_s3_bucket_ownership_controls" "bucket_ownership" {
  bucket = aws_s3_bucket.react_bucket.id
  rule {
    object_ownership = "BucketOwnerPreferred"
  }
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

# Environment file for frontend (.env)
resource "local_sensitive_file" "frontend_env" {
  count = local.local_run ? 1 : 0
  content = <<EOF
VITE_API_URL=${aws_api_gateway_stage.api_stage.invoke_url}
VITE_COGNITO_REGION=us-east-1
VITE_COGNITO_USER_POOL_ID=${aws_cognito_user_pool.user_pool.id}
VITE_COGNITO_CLIENT_ID=${aws_cognito_user_pool_client.client.id}
EOF
  filename = "${path.module}/${local.react_app_directory}/.env"
  depends_on = [
    aws_api_gateway_stage.api_stage,
    aws_cognito_user_pool.user_pool,
    aws_cognito_user_pool_client.client
  ]
}

resource "null_resource" "deploy_react_app" {
  count = local.local_run ? 1 : 0

  provisioner "local-exec" {
    command = "cd ${local.react_app_directory} && npm install && npm run build && aws s3 sync ./dist s3://${aws_s3_bucket.react_bucket.bucket} --delete && aws cloudfront create-invalidation --distribution-id ${aws_cloudfront_distribution.s3_distribution.id} --paths /*"
  }

  depends_on = [aws_s3_bucket.react_bucket, local_sensitive_file.user_pool_config, local_sensitive_file.frontend_env, aws_cloudfront_distribution.s3_distribution]
}

resource "aws_s3_bucket" "csv_bucket" {
  bucket = "${var.deploy_env}-trailcount-csv-bucket-${random_integer.random_suffix.result}"

  tags = {
    Name = "${var.deploy_env}-trailcount-csv-bucket"
  }

  force_destroy = true
}

resource "aws_s3_bucket_cors_configuration" "example" {
  bucket = aws_s3_bucket.csv_bucket.id

  cors_rule {
    allowed_origins = ["*"]
    allowed_methods = ["GET", "HEAD", "PUT", "POST", "DELETE"]
    allowed_headers = ["*"]
    expose_headers = ["ETag"]
  }
}

resource "aws_s3_bucket" "truststore_bucket" {
  bucket = "${var.deploy_env}-truststore-bucket-${random_integer.random_suffix.result}"

  tags = {
    Name = "${var.deploy_env}-truststore-bucket"
  }

  force_destroy = true
}

resource "aws_s3_bucket_policy" "truststore_policy" {
  bucket = aws_s3_bucket.truststore_bucket.id
  policy = jsonencode({
Version = "2012-10-17"
    Statement = [
      {
        Effect    = "Allow"
        Principal = {
          Service = "apigateway.amazonaws.com"
        }
        Action   = "s3:GetObject"
        Resource = "${aws_s3_bucket.truststore_bucket.arn}/truststore.pem"
      }
    ]
  })
}