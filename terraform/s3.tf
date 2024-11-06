resource "aws_s3_bucket" "bucket" {
  bucket = "${var.bucket_name}-${random_integer.random_suffix.result}"
  
  tags = {
    Name = var.bucket_name
  }

  force_destroy = true
}

resource "aws_s3_bucket_acl" "bucket_acl" {
  bucket = aws_s3_bucket.bucket.id
  acl    = var.bucket_acl
}

resource "null_resource" "deploy_react_app" {
  provisioner "local-exec" {
    command = "cd ${var.react_app_directory} && npm install && npm run build && aws s3 sync ./dist s3://${aws_s3_bucket.ecombucket.bucket} --delete"
  }

  depends_on = [aws_s3_bucket.bucket]
}
