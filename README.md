# Trail Count - Infrastructure README

This README provides instructions on how to set up and run Terraform with AWS CLI for provisioning the Trail Count infrastructure on AWS.

## Overview

The Trail Count infrastructure includes:
- **React Frontend**: Hosted on S3 with optional CloudFront CDN
- **API Gateway**: RESTful API with Cognito authentication
- **Lambda Functions**: Serverless backend for trail data management
- **DynamoDB**: NoSQL database for trails, devices, and logs
- **Cognito**: User authentication and authorization
- **CloudFront** (optional): CDN for production deployments
- **Route53** (optional): DNS management for custom domains

## Prerequisites

Make sure you have the following tools installed:

- **AWS CLI**: [Installation guide](https://aws.amazon.com/cli/)
- **Terraform**: Download from [terraform.io](https://www.terraform.io/downloads)
- **Node.js and npm**: For building the React application
- **Python 3.x**: For Lambda functions

## Quick Start

### 1. Configure AWS CLI

Ensure that the AWS CLI is configured with the appropriate credentials:

```bash
aws configure
```

You'll need:
- AWS Access Key ID
- AWS Secret Access Key
- Default region (e.g., `us-east-1`)
- Default output format (e.g., `json`)

### 2. Initialize Terraform

Navigate to the terraform directory and initialize:

```bash
cd terraform
terraform init
```

This will download necessary providers and set up the backend.

### 3. Configure Variables

Edit `variables.tf` or create `terraform.tfvars` with your configuration:

```hcl
# Basic configuration
env = "local"
bucket_name = "trailcount-bucket"
```

### 4. Apply the Terraform Configuration

Apply the configuration to create resources on AWS:

```bash
terraform apply
```

Review the plan and type `yes` to confirm.

### 5. Get Outputs

After deployment, get important URLs:

```bash
# Get website URL
terraform output website_url

# Get API Gateway URL
terraform output api_gateway_url

# Get Route53 nameservers (if using custom domain)
terraform output route53_nameservers
```

## Deployment Mode

### Production Mode (CloudFront)

- CloudFront CDN distribution
- Private S3 bucket
- HTTPS/SSL support
- Geographic restrictions
- Optimized caching

See [DEPLOYMENT_CLOUDFRONT.md](terraform/DEPLOYMENT_CLOUDFRONT.md) for detailed CloudFront setup.

## Key Variables

### Required Variables

- `env`: Default resource name prefix, should be _local_ for local runs
- `bucket_name`: S3 bucket name (if not using custom domain)

### Optional Variables

- `use_domain`: Enable custom domain (set whenever not `local` or `test` run)
- `domain`: Root domain name (e.g., `adirondackwilderness.org`)
- `sub`: Subdomain (e.g., `trailblazers-tst` for `trailblazers-tst.adirondackwilderness.org`)
- `acm_certificate_arn`: SSL certificate ARN (required if `use_domain = true`)
- `ses_identity_arn`: SES identity ARN (required if `local_run = false`)
- `local_user_email`: Email to send from (configured aws identity) (required if `local_run = true`)
- `authorization_enabled`: Enable API Gateway authorization (default: `true`)
- `users`: Users to create on startup. (default: [`root_admin`, `admin`, `trail_manager`, `user`])

## Infrastructure Components

### Frontend (React App)

- **S3 Bucket**: Stores static React application files
- **CloudFront Distribution** (optional): CDN for global content delivery
- **Route53** (optional): DNS management for custom domains

### Backend (API)

- **API Gateway**: RESTful API endpoints
- **Lambda Functions**: Serverless compute for:
  - Trail data management [public_api](lambdas/public_api)
  - Device data ingestion
  - Simulate trail data [simulate_data.py](lambdas/simulate_data.py)
  - CSV handling [csv](lambdas/public_api/csv) [csv_url](lambdas/public_api/csv_url)
  - User management [users](lambdas/public_api/users)
- **Cognito User Pool**: User authentication
- **Lambda Authorizer**: API authorization
- **DynamoDB Tables**:
  - `<env>_device_table`: Devices and all device information
  - `<env>_trail_table`: Trails and all trail information
  - `<env>_device_trail_table`: Linking between devices and trails and all link information
  - `<env>_area_table`: Areas and trails within them
  - `<env>_device_trail_log_hour_table`: Device trail logs for hourly granularity
  - `<env>_device_trail_log_day_table`: Device trail logs for daily granularity
  - `<env>_device_trail_log_week_table`: Device trail logs for weekly granularity
  - `<env>_device_trail_log_month_table`: Device trail logs for monthly granularity
  - `<env>_error_table`: Errors that have happened with the error, device, and time

## Additional Commands

```bash
# Check AWS CLI version
aws --version

# Validate Terraform configuration
terraform validate

# Format Terraform files
terraform fmt

# Show current state
terraform show

# Destroy all resources
terraform destroy
```

## Troubleshooting

### Permission Errors

Ensure that your AWS IAM user has sufficient permissions for:
- S3 (bucket creation, object upload)
- CloudFront (distribution creation)
- Route53 (hosted zone management)
- API Gateway (API creation)
- Lambda (function creation and execution)
- DynamoDB (table creation)
- Cognito (user pool creation)
- ACM (certificate management)

### Configuration Issues

- Double-check that your AWS CLI is configured correctly
- Verify region settings (CloudFront certificates must be in `us-east-1`)
- Ensure all required variables are set

### CloudFront Deployment

- CloudFront distributions take 15-20 minutes to deploy
- Wait for deployment to complete before testing
- Check CloudFront status in AWS Console

### DNS Issues

- DNS propagation can take 24-48 hours
- Verify nameservers are correctly configured at domain registrar
- Use `dig` or `nslookup` to check DNS resolution

## Documentation

- **Github Actions**: See [.github/GITHUB_ACTIONS.md](.github/GITHUB_ACTIONS.md)
- **React Frontend**: See [swen-project-react-app/REACT_FRONTEND.md](swen-project-react-app/REACT_FRONTEND.md)
- **CloudFront/Route53 Deployment**: See [terraform/DEPLOYMENT_CLOUDFRONT_ROUTE53.md](terraform/DEPLOYMENT_CLOUDFRONT_ROUTE53.md)
- **API Documentation**: See [API_DOCUMENTATION.md](API_DOCUMENTATION.md)
- **Testing**: See [tests/TESTING_OVERVIEW.md](tests/TESTING_OVERVIEW.md)
- **API Testing**: See [tests/api_tests/API_TESTING.md](tests/api_tests/API_TESTING.md)
- **UI Testing**: See [tests/ui_tests/UI_TESTING.md](tests/ui_tests/UI_TESTING.md)

## Additional Resources

- [AWS CLI Documentation](https://docs.aws.amazon.com/cli/)
- [Terraform Documentation](https://www.terraform.io/docs)
- [Terraform AWS Provider](https://registry.terraform.io/providers/hashicorp/aws/latest/docs)