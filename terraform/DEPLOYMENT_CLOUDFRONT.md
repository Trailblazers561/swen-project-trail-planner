# CloudFront and Route53 Deployment Guide

This guide explains how to configure and deploy the Trail Planner application using AWS CloudFront (CDN) for production use.

## Overview

The infrastructure supports the follwing:

   - CloudFront CDN distribution
   - Private S3 bucket (accessed only via CloudFront)
   - Custom domain for cloud runs
   - HTTPS/SSL support
   - Geographic restrictions (US/CA only)
   - Optimized caching

## Prerequisites

Before deploying with CloudFront and Route53, ensure you have:

1. **AWS Account** with appropriate permissions
2. **Domain Name** (if using custom domain)
3. **SSL Certificate** in AWS Certificate Manager (ACM) - **must be in us-east-1 region** for CloudFront

## Variables Configuration

Variables are defined in [variables.tf](variables.tf), these can be overridden to adjust when and where the site is being hosted, but should be handled automatically. By default the custom domain will be used for every environment other than `local` and `test`.

### Required Variable to Set For Custom Domain (Handled By Github Actions)

```hcl
# ACM Certificate ARN (must be in us-east-1 region)
# Get this from AWS Certificate Manager console
acm_certificate_arn = "arn:aws:acm:us-east-1:123456789012:certificate/12345678-1234-1234-1234-123456789012"
```

### Locals Automatically Set

```hcl
  # Wheter or not to use a custom domain
  use_domain = !local.local_run && !local.test_run
  # The Root Domain
  domain = "adirondackwilderness.org"
  # The Sub Domain To Prefix The Domain With
  sub_domain = "trailblazers-${var.deploy_env}"
```

### Optional Variables

```hcl
# Bucket name (only used if use_domain is false)
bucket_name = "trailplanner-bucket"
```

### Default User Account Information

The following information **should** be changed and can be found in `variables.tf` under the `users` `local`:
```hcl
  root_admin = { username = "CHANGE ME",    password = "CHANGE ME", email = "CHANGE ME" }
    admin = { username = "CHANGE ME",    password = "CHANGE ME", email = "CHANGE ME" }
    trail_manager = { username = "CHANGE ME", password = "CHANGE ME", email = "CHANGE ME" }
    user = { username = "CHANGE ME",   password = "CHANGE ME",  email = "CHANGE ME" }
```

## Step-by-Step Deployment

### Step 1: Obtain SSL Certificate (if using custom domain)

1. Go to AWS Certificate Manager (ACM) in the **us-east-1** region
2. Request a public certificate
3. Enter your domain names with specific subdomain, in this case it is all the subdomains for our environments (`trailblazers-tst.adirondackwilderness.org`, `trailblazers-uat.adirondackwilderness.org`, `trailblazers-prod.adirondackwilderness.org`)
4. Leave Disable Export
4. Choose DNS validation
6. Leave `RSA 2048` Key alogrith
5. Complete validation (add DNS records to your domain)
    1.  Open the domain registrar (In our case squarespace)
    2. Navigate to DNS -> DNS Settings
    3. Repeat the following steps for each domain
       1. Add a record under `Custom records`
       2. Enter in type: `CNAME`
       3. Enter in name: CNAME name from the AWS certificate (remove the domain from the end of what AWS provides ex. `.adirondackwilderness.org.`)
       4. Priority will be `-` and TTL can be left at `4 hrs`
       5. Enter in alias data: CNAME value from AWS certificate
       6. Click save, and leave these DNS on squarespace even after the certificate is validated (works for certificate renewal)
6. Wait for AWS to Issue the certificate, this should take ~5 minutes
6. Copy the Certificate ARN

**Important:** CloudFront requires certificates to be in the **us-east-1** region, even if your other resources are in different regions.

### Step 2: Configure Variables

Outlined above, but should work automatically. Ensure the repository has the correct certificate arn.

### Step 3: Push Code to Environment Branch

This will automatically trigger the github action to apply your changes

### Step 4: Configure DNS (if using custom domain)

After `terraform apply` completes:

1. Get the terraform apply output and look for `website_url`

2. Add your domain url to the domain registrar (In our case squarespace)
 -  Navigate to DNS -> DNS Settings
 - Add a record under `Custom records`
 - Enter in type: `CNAME`
 - Enter in name: `trailblazers-<DEPLOY_ENV>`
 - Priority will be `-` and TTL can be left at `4 hrs`
 - Enter in alias data: `website_url` from the apply
 - Wait for DNS propagation (can take up to 48 hours, usually much faster)

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

- S3 bucket is **private** (not publicly accessible)
- Only CloudFront can access the bucket via Origin Access Control
- This is the recommended production setup

### Cost Considerations

- **CloudFront**: Pay for data transfer and requests
- **ACM**: Free for public certificates
- **S3**: Standard storage and request costs
- **domain registrar**: Cost varies depending on used manager

## Troubleshooting

### CloudFront Distribution Not Accessible

1. Verify CloudFront distribution status in AWS Console
2. Wait 15-20 minutes after creation for full deployment
3. Check CloudFront logs for errors

### Custom Domain Not Working

1. Verify `acm_certificate_arn` is set
2. Check that certificate is in **us-east-1** region
3. Verify certificate is validated in ACM
4. Check custom domain cnames are configured at domain registrar
5. Wait for DNS propagation (use `dig your-domain.com` to check)

### SSL Certificate Issues

1. Ensure certificate is in **us-east-1** region
2. Verify certificate is validated and active
3. Check certificate covers your domain (e.g., `trailblazers-tst.adirondackwilderness.com`)
4. For wildcard certificates, ensure format is `*.adirondackwilderness.com`

### Cloudfront Site Not Updating After Changes Applied

Cloudfront caches the information from the bucket so that it doesn't need to query the bucket every time. When this happens you need to create an invalidation in the distribution to tell cloudfront to look at the bucket again.

To do this in the AWS Console (web application):
1. Navigate to the specific cloudfront distribution
2. Go to the invalidations tab and click _Create invalidation_
3. Set the path to /* and click _Create invalidation_

To do this in the command line:
If you are logged into the account with the distribution run the following command:

```aws cloudfront create-invalidation --distribution-id <DISTRIBUTION_ID> --paths "/*"```

If you are not logged into the account with the distribution, create a profile that is logged into the account and run:

```aws cloudfront create-invalidation --distribution-id <DISTRIBUTION_ID> --paths "/*" --profile <PROFILE_NAME>```

## Security Best Practices

1. **Always use CloudFront in production**
2. **Keep S3 bucket private** when using CloudFront
3. **Use custom domain with SSL** for production
4. **Enable geographic restrictions** (already configured for US/CA)
5. **Monitor CloudFront access logs** for security analysis
6. **Regularly update SSL certificates** before expiration