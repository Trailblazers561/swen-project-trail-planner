# Terraform with AWS CLI - README
This README provides instructions on how to set up and run Terraform with AWS CLI for provisioning infrastructure on AWS.

## Prerequisites
Make sure you have the following tools installed:

### AWS CLI: To install, follow AWS CLI installation guide.
### Terraform: Download and install the latest version from the Terraform website.

Getting Started

1. Configure AWS CLI
Ensure that the AWS CLI is configured with the appropriate credentials:

`aws configure`

2. Initialize Terraform
In the directory containing your Terraform configuration files (e.g., main.tf), initialize the project:

`terraform init`

This will download necessary providers and set up the backend if specified.

3. Apply the Terraform Configuration
Apply the configuration to create or update resources on AWS:

`terraform apply`

4. Destroy Resources
When you no longer need the infrastructure, use the following command to delete it:

`terraform destroy`

## Additional Commands
Check AWS CLI Version: `aws --version`

Validate Terraform Configuration: `terraform validate`

Format Terraform Files: `terraform fmt`\

**Troubleshooting**

Permission Errors: Ensure that your AWS IAM user has sufficient permissions for the resources you’re provisioning.

Configuration Issues: Double-check that your AWS CLI is configured correctly if you encounter connectivity issues.

For more details, refer to the official AWS CLI documentation and Terraform documentation.

## Device Trail Assignment
The `/devices` API automatically handles device-to-trail linking without requiring manual registration:

- **New devices**: Automatically assigned to trail_id 0 on first use
- **Existing devices**: Server looks up the most recent trail assignment from previous data
- **Trail updates**: Include `trail_id` in the payload to change a device's trail assignment
- **Caching**: Trail assignments are automatically cached in DeviceMetadata for faster lookups
