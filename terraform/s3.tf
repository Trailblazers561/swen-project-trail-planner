resource "aws_s3_bucket" "bucket" {
  bucket = local.use_domain ? "${local.sub_domain}.${local.domain}" : "${var.deploy_env}-${var.bucket_name}-${random_integer.random_suffix.result}"

  tags = {
    Name = "${var.deploy_env}-${var.bucket_name}"
  }

  force_destroy = true
}

output "react_bucket_name" {
  value = aws_s3_bucket.bucket.bucket
}

resource "aws_s3_bucket_ownership_controls" "bucket_ownership" {
  bucket = aws_s3_bucket.bucket.id
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