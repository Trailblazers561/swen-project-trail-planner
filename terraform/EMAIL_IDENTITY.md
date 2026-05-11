# Email Identity Setup Guide

This guide talks about the custom SES identity used to send emails with AWS. The identity is created in an AWS account and not managed by terraform.

## AWS Creation

1. Navigate to `Amazon SES`in the AWS console
2. Create an identity and select `domain`
3. Enter appropriate domain/subdomain ie. `trailplanner-auth.adirondackwilderness.org`
4. Leave the following selects unchecked: `Assign a default configuration set` and `Assign to a tenant`
5. Check `Use a custom MAIL FROM domain`
   - Enter mail from domain ie. `mail`
   - Uncheck `Publish DNS records to Route53` `Enabled` as we don't use Route53
6. Select `Easy DKIM` for verification method
   - Select `RSA_2048_BIT` for `DKIM signing key length`
   - Uncheck `Publish DNS records to Route53` `Enabled` as we don't use Route53
7. Create identity
8. You will now need to verify all of the different "things" in your chosen domain registrar

## Squarespace Setup

 - AWS will provide you with each DNS record you need to create in Squarespace custom DNS records
 - There will likely be three `CNAME` records for `DomainKeys Identified Mail (DKIM)`
 - There will likely be one `MX` record and one `TXT` record for `Custom MAIL FROM domain`
 - There will likely be one `TXT` record for `Domain-based Message Authentication, Reporting, and Conformance (DMARC)`
 - For `CNAME` records 
   - Select `CNAME` for type
   - Enter the specified subdomain in the name field (omitting `.adirondackwilderness.org`)
   - Leave TTL as the default (`4 hrs`)
   - Enter the value provided by aws in the data section
 - For `MX` records
   - Select `MX` for type
   - Enter the specified subdomain in the name field (omitting `.adirondackwilderness.org`)
   - Enter the first number in the AWS value in the priority section (ie. `10`)
   - Leave TTL as the default (`4 hrs`)
   - Enter the second part in the AWS value in the data section
 - For `TXT` records
   - Select `TXT` for type
   - Enter the specified subdomain in the name field (omitting `.adirondackwilderness.org`)
   - Leave TTL as the default (`4 hrs`)
   - Enter the specified value in the data section (omitting quotation marks)
 - AWS will automatically verifiy the identity if everything is setup correctly

## Troubleshooting

 - Ensure all custom DNS records match AWS expectation when entering
 - Do not restate the domain in the name field for custom records
 - By default AWS is in sandbox mode, where it will only send emails to verified identities
   - AWS will say everything worked properly and not send the email if this is the case
   - To stay in sandbox mode add your email as a verified email identity in SES
   - You can leave sandbox mode in the SES `Account Dashboard, this takes some time for AWS to process
 - Ensure the identity arn matches what is passed into terraform (either from terraform.tfvars or in repository variables from the pipeline)