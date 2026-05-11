# Trail Planner - Infrastructure README

This README provides instructions on how to set up and run Terraform with AWS CLI for provisioning the Trail Planner infrastructure on AWS.

## Overview

The Trail Planner infrastructure includes:
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
default_name = "trailplanner"
bucket_name = "trailplanner-bucket"
react_app_directory = "../swen-project-react-app"

# For CloudFront deployment (see DEPLOYMENT_CLOUDFRONT_ROUTE53.md)
has_cdn = false  # Set to true for production
has_domain = false  # Set to true if using custom domain
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

## Deployment Modes

### Development/Testing Mode (Default)

- Direct S3 website hosting
- Public bucket access
- No CDN
- Fast deployment for testing

**Configuration:**
```hcl
has_cdn = false
```

### Production Mode (CloudFront)

- CloudFront CDN distribution
- Private S3 bucket
- HTTPS/SSL support
- Geographic restrictions
- Optimized caching

**Configuration:**
```hcl
has_cdn = true
has_domain = false  # or true for custom domain
```

See [DEPLOYMENT_CLOUDFRONT_ROUTE53.md](terraform/DEPLOYMENT_CLOUDFRONT_ROUTE53.md) for detailed CloudFront/Route53 setup.

## Key Variables

### Required Variables

- `default_name`: Default resource name prefix
- `bucket_name`: S3 bucket name (if not using custom domain)
- `react_app_directory`: Path to React application directory

### Optional Variables

- `has_cdn`: Enable CloudFront CDN (default: `false`)
- `has_domain`: Enable custom domain with Route53 (default: `false`)
- `domain`: Root domain name (e.g., `example.com`)
- `sub`: Subdomain (e.g., `adiron` for `adiron.example.com`)
- `acm_certificate_arn`: SSL certificate ARN (required if `has_domain = true`)
- `bucket_acl`: S3 bucket ACL (`private` for CloudFront, `public-read` for S3 website)
- `authorization_type`: API Gateway authorization (`COGNITO_USER_POOLS` or `NONE`)

## Infrastructure Components

### Frontend (React App)

- **S3 Bucket**: Stores static React application files
- **CloudFront Distribution** (optional): CDN for global content delivery
- **Route53** (optional): DNS management for custom domains

### Backend (API)

- **API Gateway**: RESTful API endpoints
- **Lambda Functions**: Serverless compute for:
  - Trail data management (`traildata.py`)
  - Device data ingestion
- **Cognito User Pool**: User authentication
- **DynamoDB Tables**:
  - `TrailDeviceLogs`: Trail sensor data (detection timestamps per trail)
  - `TrailMetadata`: Trail information and GPS coordinates
  - `TrailGroups`: Wilderness area groupings
  - `DeviceMetadata`: Device-to-trail associations and last-seen telemetry
  - `DeviceCallLog`: Per-call-in telemetry history (firmware version, battery, signal quality, record count)

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

- **CloudFront/Route53 Deployment**: See [terraform/DEPLOYMENT_CLOUDFRONT_ROUTE53.md](terraform/DEPLOYMENT_CLOUDFRONT_ROUTE53.md)
- **API Documentation**: See [API_DOCUMENTATION.md](API_DOCUMENTATION.md)
- **API Tests**: See [swen-project-react-app-API-tests/completed/README.md](swen-project-react-app-API-tests/completed/README.md)
- **UI Tests**: See [swen-project-react-app-UI-tests/completed/README.md](swen-project-react-app-UI-tests/completed/README.md)

## Device Trail Assignment

The `/devices` API automatically handles device-to-trail linking without requiring manual registration:

- **New devices**: Automatically assigned to trail_id 0 on first use
- **Existing devices**: Server looks up trail assignment from DeviceMetadata, then falls back to the most recent log entry
- **Trail updates**: Include `trail_id` in the payload to change a device's trail assignment
- **Dashboard**: Device View (formerly "List View") shows all devices with inline trail assignment — unassociated devices appear at the top with an "Assign Trail" dropdown; associated devices show a pencil button to reassign or unassign inline, without a modal

## Additional Resources

- [AWS CLI Documentation](https://docs.aws.amazon.com/cli/)
- [Terraform Documentation](https://www.terraform.io/docs)
- [Terraform AWS Provider](https://registry.terraform.io/providers/hashicorp/aws/latest/docs)
