# CloudFront and Route53 Deployment Guide

This guide explains how to configure and deploy the TrailCount webapp (formerly "Trail Planner") using AWS CloudFront (CDN) and Route53 (DNS) for production use.

> **Note:** Post-cutover (2026-05-15), TrailCount tenant stacks (`adk-test`, `adk-prod`, `demo-test`, `demo-prod`) use CloudFront + ACM + API Gateway custom domains wired automatically by Terraform when `manage_dns = true`. See `../CLAUDE.md` and `../../TERRAFORM_A2.md` for the tenant-scoped workflow. DNS lives in **Squarespace, not Route 53** (Route 53 is empty in this account). The Route53 sections below were written for the legacy V1 era and are retained for reference only.

## Overview

The infrastructure supports two deployment modes:

1. **Development/Testing Mode** (`has_cdn = false`):
   - Direct S3 website hosting
   - Public bucket access
   - No CDN optimization
   - Suitable for testing

2. **Production Mode** (`has_cdn = true`):
   - CloudFront CDN distribution
   - Private S3 bucket (accessed only via CloudFront)
   - Optional custom domain with Route53
   - HTTPS/SSL support
   - Geographic restrictions (US/CA only)
   - Optimized caching

## Prerequisites

Before deploying with CloudFront and Route53, ensure you have:

1. **AWS Account** with appropriate permissions
2. **Domain Name** (if using custom domain)
3. **SSL Certificate** in AWS Certificate Manager (ACM) - **must be in us-east-1 region** for CloudFront
4. **Terraform** installed and configured
5. **AWS CLI** configured with credentials

## Variables Configuration

Edit `terraform/variables.tf` or use `terraform.tfvars` to set the following variables:

### Required Variables for CloudFront

```hcl
# Enable CloudFront CDN
has_cdn = true
```

### Required Variables for Custom Domain (Route53)

If you want to use a custom domain with Route53:

```hcl
# Enable custom domain
has_domain = true

# Your root domain (e.g., "example.com")
domain = "example.com"

# Subdomain (e.g., "adiron" for adiron.example.com)
sub = "adiron"

# ACM Certificate ARN (must be in us-east-1 region)
# Get this from AWS Certificate Manager console
acm_certificate_arn = "arn:aws:acm:us-east-1:123456789012:certificate/12345678-1234-1234-1234-123456789012"
```

### Optional Variables

```hcl
# Bucket name (only used if has_domain is false)
bucket_name = "trailplanner-bucket"

# Bucket ACL when using CloudFront (should be "private")
bucket_acl = "private"
```

### Default User Account Information

The following information **should** be changed and can be found in `cognito.tf` under the `admin` `aws_cognito_user`:
```hcl
  username     = "CHANGE ME"
  password     = "CHANGE ME"
  attributes = {
    email      = "CHANGE ME"
  }
```

## Step-by-Step Deployment

### Step 1: Obtain SSL Certificate (if using custom domain)

1. Go to AWS Certificate Manager (ACM) in the **us-east-1** region
2. Request a public certificate
3. Enter your domain name (e.g., `adiron.example.com`)
4. Choose DNS validation
5. Complete validation (add DNS records to your domain)
6. Copy the Certificate ARN

**Important:** CloudFront requires certificates to be in the **us-east-1** region, even if your other resources are in different regions.

### Step 2: Configure Variables

Create a `terraform.tfvars` file or update `variables.tf`:

```hcl
# Enable CloudFront
has_cdn = true

# If using custom domain
has_domain = true
domain = "example.com"
sub = "adiron"
acm_certificate_arn = "[acm_certificate_arn]"

# Optional
bucket_acl = "private"
```

### Step 3: Initialize Terraform

```bash
cd terraform
terraform init
```

### Step 4: Plan Deployment

```bash
terraform plan
```

Review the plan to ensure:
- CloudFront distribution will be created
- Route53 hosted zone will be created (if `has_domain = true`)
- S3 bucket will be private
- CloudFront Origin Access Control will be configured

### Step 5: Apply Configuration

```bash
terraform apply
```

This will:
1. Create/update S3 bucket (private if `has_cdn = true`)
2. Deploy React app to S3
3. Create CloudFront distribution
4. Create Route53 hosted zone (if `has_domain = true`)
5. Create Route53 A record pointing to CloudFront
6. Configure S3 bucket policy for CloudFront access

### Step 6: Configure DNS (if using custom domain)

After `terraform apply` completes:

1. Get the Route53 nameservers:
   ```bash
   terraform output route53_nameservers
   ```

2. Update your domain's nameservers at your domain registrar:
   - Go to your domain registrar (e.g., GoDaddy, Namecheap, Route53)
   - Update the nameservers to the values from the output
   - Wait for DNS propagation (can take up to 48 hours, usually much faster)

### Step 7: Get Your Website URL

After deployment, get your website URL:

```bash
terraform output website_url
```

This will output:
- `https://adiron.example.com` (if using custom domain)
- `https://d1234567890abc.cloudfront.net` (if using CloudFront without custom domain)
- `http://bucket-name.s3-website-us-east-1.amazonaws.com` (if not using CloudFront)

## Configuration Options

### CloudFront Settings

The CloudFront distribution is configured with:

- **Price Class**: `PriceClass_100` (US and EU edge locations only)
- **Geographic Restrictions**: Whitelist for US and CA only
- **Caching**:
  - Default: 1 hour TTL
  - `/content/immutable/*`: 1 year TTL (for static assets)
  - `/content/*`: 1 hour TTL
- **Error Handling**: 403 errors redirect to `/index.html` (for React Router)
- **HTTPS**: Always redirects HTTP to HTTPS
- **IPv6**: Enabled

### Route53 Configuration

When `has_domain = true` and `has_cdn = true`:

- Creates a Route53 hosted zone for your domain
- Creates an A record (alias) pointing to CloudFront
- Outputs nameservers that must be configured at your domain registrar

## Important Notes

### Certificate Requirements

- **Must be in us-east-1 region** for CloudFront
- Can be requested in ACM or imported
- Must be validated before use
- Supports wildcard certificates (e.g., `*.example.com`)

### DNS Propagation

- DNS changes can take 24-48 hours to propagate globally
- Usually propagates within a few hours
- Use `dig` or `nslookup` to check propagation status

### CloudFront Deployment Time

- CloudFront distribution creation takes 15-20 minutes
- Updates to CloudFront can take 15-20 minutes to deploy
- Use `terraform apply` and wait for completion

### S3 Bucket Security

When `has_cdn = true`:
- S3 bucket is **private** (not publicly accessible)
- Only CloudFront can access the bucket via Origin Access Control
- This is the recommended production setup

### Cost Considerations

- **CloudFront**: Pay for data transfer and requests
- **Route53**: $0.50 per hosted zone per month + query costs
- **ACM**: Free for public certificates
- **S3**: Standard storage and request costs

## Troubleshooting

### CloudFront Distribution Not Accessible

1. Check that `has_cdn = true` in your variables
2. Verify CloudFront distribution status in AWS Console
3. Wait 15-20 minutes after creation for full deployment
4. Check CloudFront logs for errors

### Custom Domain Not Working

1. Verify `has_domain = true` and `acm_certificate_arn` is set
2. Check that certificate is in **us-east-1** region
3. Verify certificate is validated in ACM
4. Check Route53 nameservers are configured at domain registrar
5. Wait for DNS propagation (use `dig your-domain.com` to check)

### SSL Certificate Issues

1. Ensure certificate is in **us-east-1** region
2. Verify certificate is validated and active
3. Check certificate covers your domain (e.g., `adiron.example.com`)
4. For wildcard certificates, ensure format is `*.example.com`

### Route53 Nameserver Configuration

1. Get nameservers: `terraform output route53_nameservers`
2. Update at your domain registrar
3. Wait for DNS propagation
4. Verify with: `dig NS your-domain.com`

## Example terraform.tfvars

```hcl
# Enable CloudFront CDN
has_cdn = true

# Enable custom domain with Route53
has_domain = true
domain = "example.com"
sub = "adiron"

# ACM Certificate ARN (must be in us-east-1)
acm_certificate_arn = "arn:aws:acm:us-east-1:123456789012:certificate/12345678-1234-1234-1234-123456789012"

# Bucket settings
bucket_acl = "private"
bucket_name = "trailplanner-bucket"

# React app path
react_app_directory = "../swen-project-react-app"
```

## Switching Between Modes

### From S3 Website to CloudFront

1. Set `has_cdn = true` in variables
2. Run `terraform apply`
3. Update any URLs/configurations to use the new CloudFront URL

### From CloudFront to S3 Website

1. Set `has_cdn = false` in variables
2. Run `terraform apply`
3. Note: This will destroy the CloudFront distribution

### Adding Custom Domain to Existing CloudFront

1. Obtain SSL certificate in us-east-1
2. Set `has_domain = true`, `domain`, `sub`, and `acm_certificate_arn`
3. Run `terraform apply`
4. Configure nameservers at domain registrar

## Outputs

After deployment, use these commands to get important information:

```bash
# Get website URL
terraform output website_url

# Get Route53 nameservers (if using custom domain)
terraform output route53_nameservers

# Get API Gateway URL
terraform output api_gateway_url
```

## Security Best Practices

1. **Always use CloudFront in production** (`has_cdn = true`)
2. **Keep S3 bucket private** when using CloudFront
3. **Use custom domain with SSL** for production
4. **Enable geographic restrictions** (already configured for US/CA)
5. **Monitor CloudFront access logs** for security analysis
6. **Regularly update SSL certificates** before expiration