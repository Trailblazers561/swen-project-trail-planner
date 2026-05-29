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
yum install -y docker --skip-broken
service docker start
systemctl enable docker
usermod -aG docker ec2-user
mkdir -p /opt/ca_instance
aws ecr get-login-password --region ${data.aws_region.current.name} | docker login --username AWS --password-stdin ${aws_ecr_repository.step_ca.registry_id}.dkr.ecr.${data.aws_region.current.name}.amazonaws.com
docker pull ${aws_ecr_repository.step_ca.repository_url}:${var.step_ca_version}
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
Before=docker.service
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