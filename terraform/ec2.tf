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
    yum update -y
    yum install -y docker
    service docker start
    systemctl enable docker
    usermod -aG docker ec2-user
    mkdir -p /opt/ca_instance
  EOF

  tags = {
    Name = "${var.deploy_env}_ca_instance"
  }
}

output "ca_instance_private_ip" {
  value       = aws_instance.ca_instance.private_ip
  description = "Private ip used as as STEP_CA_URL for lambdas"
}

output "ca_instance_id" {
  value = aws_instance.ca_instance.id
}