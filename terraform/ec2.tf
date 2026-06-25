data "aws_ami" "amazon_linux_2023" {
  most_recent = true
  owners      = ["amazon"]

  filter {
    name   = "name"
    values = ["al2023-ami-*-x86_64"]
  }
}

resource "aws_instance" "ca_instance" {
  ami                    = data.aws_ami.amazon_linux_2023.id
  instance_type          = "t3.small"
  subnet_id              = aws_subnet.private_subnet.id
  vpc_security_group_ids = [aws_security_group.ca_sg.id]
  iam_instance_profile   = aws_iam_instance_profile.ca_instance_profile.name

  root_block_device {
    volume_size           = 30
    volume_type           = "gp3"
    encrypted             = true
    delete_on_termination = true
  }

user_data = <<-EOF
#!/bin/bash
set -e
yum update -y --skip-broken
yum install -y docker amazon-ecr-credential-helper --skip-broken
yum install -y amazon-ssm-agent --skip-broken
yum install -y python3-pip --skip-broken
service docker start
systemctl enable docker
systemctl enable amazon-ssm-agent
systemctl start amazon-ssm-agent
usermod -aG docker ec2-user

# make docker use ecr credential helper
mkdir -p /root/.docker
cat > /root/.docker/config.json <<'DOCKERCONFIG'
{
  "credHelpers": {
    "${aws_ecr_repository.step_ca.registry_id}.dkr.ecr.${data.aws_region.current.name}.amazonaws.com": "ecr-login"
  }
}
DOCKERCONFIG

# ensure ebs mount finishes before moving on
mkdir -p /opt/ca_instance
chmod 777 /opt/ca_instance
cat > /usr/local/bin/wait-for-ebs.sh <<'SCRIPT'
#!/bin/bash
until [ -b /dev/nvme1n1 ]; do sleep 2; done
SCRIPT
cat > /usr/local/bin/mount-ca-data.sh <<'SCRIPT'
#!/bin/bash
if ! blkid -t TYPE=xfs /dev/nvme1n1; then
  mkfs -t xfs /dev/nvme1n1
fi
mkdir -p /opt/ca_instance
chmod 777 /opt/ca_instance
mount /dev/nvme1n1 /opt/ca_instance
UUID=$(blkid -s UUID -o value /dev/nvme1n1)
grep -q "$UUID" /etc/fstab || echo "UUID=$UUID /opt/ca_instance xfs defaults,nofail 0 2" >> /etc/fstab
SCRIPT
chmod +x /usr/local/bin/wait-for-ebs.sh
chmod +x /usr/local/bin/mount-ca-data.sh
cat > /etc/systemd/system/mount-ca-data.service <<'UNIT'
[Unit]
Description=Mount CA data EBS volume
After=local-fs.target
[Service]
Type=oneshot
RemainAfterExit=yes
ExecStartPre=/usr/local/bin/wait-for-ebs.sh
ExecStart=/usr/local/bin/mount-ca-data.sh
[Install]
WantedBy=multi-user.target
UNIT
systemctl daemon-reload
systemctl enable mount-ca-data.service
systemctl start mount-ca-data.service
chown -R 1000:1000 /opt/ca_instance

# ensure ecr endpoint is ready to go before moving on
until aws ecr describe-repositories --region ${data.aws_region.current.name} > /dev/null 2>&1; do
  echo "Waiting for ECR endpoint..."
  sleep 10
done

# pull step-ca image, inelegant retry loop to ensure the "other part" of the ecr endpoint is ready to go. 2 minutes and change should be sufficient.
for i in 1 2 3 4 5; do
  docker pull ${aws_ecr_repository.step_ca.repository_url}:${var.step_ca_version} && break
  echo "docker pull failed, attempt number $i, retrying in 30 secs"
  sleep 30
done

# ensure secrets manager endpoint is ready to go before moving on, uses a generic command that should always work if the endpoint is functional
until aws secretsmanager get-random-password --region ${data.aws_region.current.name} > /dev/null 2>&1; do
  echo "Waiting for Secrets Manager endpoint..."
  sleep 10
done

# check if secretsmanager has our secrets present, restore if so, else generate fresh and upload secrets
if aws secretsmanager describe-secret --secret-id "cert-auth/root-ca-cert" --region ${data.aws_region.current.name} > /dev/null 2>&1; then
  mkdir -p /opt/ca_instance/certs
  mkdir -p /opt/ca_instance/secrets
  mkdir -p /opt/ca_instance/config
  mkdir -p /opt/ca_instance/db

  aws secretsmanager get-secret-value --secret-id "cert-auth/root-ca-cert" --region ${data.aws_region.current.name} --query SecretString --output text > /opt/ca_instance/certs/root_ca.crt
  aws secretsmanager get-secret-value --secret-id "cert-auth/intermediate-ca-cert" --region ${data.aws_region.current.name} --query SecretString --output text > /opt/ca_instance/certs/intermediate_ca.crt
  aws secretsmanager get-secret-value --secret-id "cert-auth/root-ca-key" --region ${data.aws_region.current.name} --query SecretString --output text > /opt/ca_instance/secrets/root_ca_key
  aws secretsmanager get-secret-value --secret-id "cert-auth/intermediate-ca-key" --region ${data.aws_region.current.name} --query SecretString --output text > /opt/ca_instance/secrets/intermediate_ca_key
  aws secretsmanager get-secret-value --secret-id "cert-auth/ca-config" --region ${data.aws_region.current.name} --query SecretString --output text > /opt/ca_instance/config/ca.json
  aws secretsmanager get-secret-value --secret-id "cert-auth/ca-password" --region ${data.aws_region.current.name} --query SecretString --output text > /opt/ca_instance/password
  aws secretsmanager get-secret-value --secret-id "cert-auth/intermediate-ca-password" --region ${data.aws_region.current.name} --query SecretString --output text > /opt/ca_instance/intermediate_password

  chmod 644 /opt/ca_instance/password
  chmod 644 /opt/ca_instance/intermediate_password
  chown -R 1000:1000 /opt/ca_instance

else
  # wipe any data that may be there from a taint->apply on the ec2 instance
  rm -rf /opt/ca_instance/*
  chown -R 1000:1000 /opt/ca_instance

  # generate passwords
  openssl rand -base64 32 > /opt/ca_instance/password
  chmod 644 /opt/ca_instance/password
  openssl rand -base64 32 > /opt/ca_instance/intermediate_password
  chmod 644 /opt/ca_instance/intermediate_password

  # initialize step-ca
  docker run --rm -v /opt/ca_instance:/home/step ${aws_ecr_repository.step_ca.repository_url}:${var.step_ca_version} step ca init --name "YourOrg CA" --dns "localhost" --address ":9000" --provisioner "device-provisioner" --password-file "/home/step/password" --provisioner-password-file "/home/step/password"
  # change intermediate key password
  docker run --rm -e TERM=dumb -v /opt/ca_instance:/home/step ${aws_ecr_repository.step_ca.repository_url}:${var.step_ca_version} step crypto change-pass /home/step/secrets/intermediate_ca_key --password-file /home/step/password --new-password-file /home/step/intermediate_password --force

python3 <<'PY'
import json

path = "/opt/ca_instance/config/ca.json"

with open(path, "r") as f:
    cfg = json.load(f)

for p in cfg["authority"]["provisioners"]:
    if p["name"] == "device-provisioner":
        p["claims"] = {
            "minTLSCertDuration": "5m",
            "defaultTLSCertDuration": "720h",
            "maxTLSCertDuration": "2160h"
        }

with open(path, "w") as f:
    json.dump(cfg, f, indent=2)

PY

  # back up to secrets manager
  secret_put() {
  aws secretsmanager describe-secret --secret-id "$1" --region ${data.aws_region.current.name} 2>/dev/null && aws secretsmanager put-secret-value --secret-id "$1" --secret-string "$2" --region ${data.aws_region.current.name} || aws secretsmanager create-secret --name "$1" --secret-string "$2" --region ${data.aws_region.current.name}
  }
  secret_put "cert-auth/ca-password" "$(cat /opt/ca_instance/password)"
  secret_put "cert-auth/intermediate-ca-password" "$(cat /opt/ca_instance/intermediate_password)"
  secret_put "cert-auth/root-ca-key" "$(cat /opt/ca_instance/secrets/root_ca_key)"
  secret_put "cert-auth/intermediate-ca-key" "$(cat /opt/ca_instance/secrets/intermediate_ca_key)"
  secret_put "cert-auth/root-ca-cert" "$(cat /opt/ca_instance/certs/root_ca.crt)"
  secret_put "cert-auth/intermediate-ca-cert" "$(cat /opt/ca_instance/certs/intermediate_ca.crt)"
  secret_put "cert-auth/ca-config" "$(cat /opt/ca_instance/config/ca.json)"
fi

# step-ca is picky about the password location when running it how i am below, needs to be in this place
cp /opt/ca_instance/intermediate_password /opt/ca_instance/secrets/password
chown 1000:1000 /opt/ca_instance/secrets/password
chmod 644 /opt/ca_instance/secrets/password

# upload root and intermediate certificates to truststore s3 bucket
until aws s3 ls s3://${aws_s3_bucket.truststore_bucket.bucket}/ > /dev/null 2>&1; do
  echo "Waiting for S3 endpoint..."
  sleep 10
done
cat /opt/ca_instance/certs/root_ca.crt /opt/ca_instance/certs/intermediate_ca.crt > /tmp/truststore.pem
aws s3 cp /tmp/truststore.pem s3://${aws_s3_bucket.truststore_bucket.bucket}/truststore.pem

# start step-ca
docker run -d --name step-ca --restart always -v /opt/ca_instance:/home/step -p 9000:9000 ${aws_ecr_repository.step_ca.repository_url}:${var.step_ca_version}
EOF

  tags = {
    Name = "${var.deploy_env}_ca_instance"
  }

  depends_on = [null_resource.push_step_ca_image]

}

output "ca_instance_private_ip" {
  value       = aws_instance.ca_instance.private_ip
  description = "Private ip used as as STEP_CA_URL for lambdas"
}

output "ca_instance_id" {
  value = aws_instance.ca_instance.id
}