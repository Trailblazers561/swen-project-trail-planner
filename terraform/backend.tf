# Remote state in S3 with DynamoDB-backed locking.
#
# Bucket + lock table were created out-of-band via AWS CLI on 2026-05-18 (the
# chicken-and-egg: you can't terraform a state-storage bucket from inside its
# own state). If you ever need to recreate them:
#
#   aws s3api create-bucket --bucket tc-tfstate-650244845886 --region us-east-1
#   aws s3api put-bucket-versioning --bucket tc-tfstate-650244845886 \
#     --versioning-configuration Status=Enabled
#   aws s3api put-bucket-encryption --bucket tc-tfstate-650244845886 \
#     --server-side-encryption-configuration \
#       '{"Rules":[{"ApplyServerSideEncryptionByDefault":{"SSEAlgorithm":"AES256"}}]}'
#   aws s3api put-public-access-block --bucket tc-tfstate-650244845886 \
#     --public-access-block-configuration \
#       BlockPublicAcls=true,IgnorePublicAcls=true,BlockPublicPolicy=true,RestrictPublicBuckets=true
#   aws dynamodb create-table --table-name tc-terraform-locks \
#     --attribute-definitions AttributeName=LockID,AttributeType=S \
#     --key-schema AttributeName=LockID,KeyType=HASH \
#     --billing-mode PAY_PER_REQUEST --region us-east-1
#
# With workspaces enabled, state lives at:
#   s3://tc-tfstate-650244845886/env/<workspace>/webapp/terraform.tfstate
terraform {
  backend "s3" {
    bucket               = "tc-tfstate-650244845886"
    key                  = "webapp/terraform.tfstate"
    region               = "us-east-1"
    dynamodb_table       = "tc-terraform-locks"
    encrypt              = true
    workspace_key_prefix = "env"
  }
}
