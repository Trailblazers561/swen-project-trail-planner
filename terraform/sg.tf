resource "aws_security_group" "lambda_sg" {
  name        = "${var.deploy_env}-lambda-sg"
  description = "sg for lambda access"
  vpc_id      = aws_vpc.cert_vpc.id

  egress {
    from_port   = 0
    to_port     = 0
    protocol    = "-1"
    cidr_blocks = ["0.0.0.0/0"]
  }

  tags = {
    Name = "${var.deploy_env}_lambda_sg"
  }
}

resource "aws_security_group" "ca_sg" {
  name        = "${var.deploy_env}-ca-sg"
  description = "ca access from lambda"
  vpc_id      = aws_vpc.cert_vpc.id

  ingress {
    description = "connection to CA from lambda"
    from_port   = 9000
    to_port     = 9000
    protocol    = "tcp"
    security_groups = [aws_security_group.lambda_sg.id]
  }

  egress {
    from_port   = 0
    to_port     = 0
    protocol    = "-1"
    cidr_blocks = ["0.0.0.0/0"]
  }

  tags = {
    Name = "${var.deploy_env}-ca-sg"
  }
}

resource "null_resource" "nuke_enis" {
  triggers = {
    subnet_id = aws_subnet.private_subnet.id
    sg_id     = aws_security_group.ca_sg.id
  }

  provisioner "local-exec" {
    when       = destroy
    interpreter = ["python3", "-c"]
    command    = <<EOT
import subprocess, json, time
result = subprocess.run(['aws', 'ec2', 'describe-network-interfaces', '--filters', 'Name=subnet-id,Values=${self.triggers.subnet_id}', '--query', 'NetworkInterfaces[*].NetworkInterfaceId', '--output', 'json'], capture_output=True, text=True)
if not result.stdout.strip():
    print("No ENIs found or AWS CLI error")
    print("stderr:", result.stderr)
    exit(0)
enis = json.loads(result.stdout)
if not enis:
    print("No ENIs to delete")
    exit(0)
for eni in enis:
    for attempt in range(40):
        r = subprocess.run(['aws', 'ec2', 'delete-network-interface', '--network-interface-id', eni], capture_output=True, text=True)
        if r.returncode == 0:
            break
        if 'currently in use' in r.stderr:
            print(f'ENI {eni} in use, waiting...')
            time.sleep(15)
        else:
            break
EOT
  }

  depends_on = [aws_subnet.private_subnet, aws_security_group.ca_sg]
}

resource "aws_security_group" "vpce_sg" {
  name        = "${var.deploy_env}-vpce-sg"
  description = "connection for ssm endpoints"
  vpc_id      = aws_vpc.cert_vpc.id

  ingress {
    from_port   = 443
    to_port     = 443
    protocol    = "tcp"
    cidr_blocks = [aws_vpc.cert_vpc.cidr_block]
  }

  ingress {
    from_port       = 443
    to_port         = 443
    protocol        = "tcp"
    security_groups = [aws_security_group.ca_sg.id]
  }

  egress {
    from_port   = 0
    to_port     = 0
    protocol    = "-1"
    cidr_blocks = ["0.0.0.0/0"]
  }
}

locals {
  ssm_endpoints = toset(["ssm", "ssmmessages", "ec2messages"])
}

resource "aws_vpc_endpoint" "ssm" {
  for_each            = local.ssm_endpoints
  vpc_id              = aws_vpc.cert_vpc.id
  service_name        = "com.amazonaws.${data.aws_region.current.name}.${each.value}"
  vpc_endpoint_type   = "Interface"
  subnet_ids          = [aws_subnet.private_subnet.id]
  security_group_ids  = [aws_security_group.vpce_sg.id]
  private_dns_enabled = true

  tags = {
    Name = "${var.deploy_env}_${each.value}_endpoint"
  }
}

resource "aws_vpc_endpoint" "ecr_api" {
  vpc_id              = aws_vpc.cert_vpc.id
  service_name        = "com.amazonaws.${data.aws_region.current.name}.ecr.api"
  vpc_endpoint_type   = "Interface"
  subnet_ids          = [aws_subnet.private_subnet.id]
  security_group_ids  = [aws_security_group.vpce_sg.id]
  private_dns_enabled = true
  tags = {
    Name = "${var.deploy_env}_ecr_api_endpoint"
  }
}

resource "aws_vpc_endpoint" "ecr_dkr" {
  vpc_id              = aws_vpc.cert_vpc.id
  service_name        = "com.amazonaws.${data.aws_region.current.name}.ecr.dkr"
  vpc_endpoint_type   = "Interface"
  subnet_ids          = [aws_subnet.private_subnet.id]
  security_group_ids  = [aws_security_group.vpce_sg.id]
  private_dns_enabled = true
  tags = {
    Name = "${var.deploy_env}_ecr_dkr_endpoint"
  }
}