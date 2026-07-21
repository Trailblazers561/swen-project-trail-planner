resource "aws_security_group" "lambda_sg" {
  name        = "${var.deploy_env}-lambda-sg"
  description = "sg for lambda access"
  vpc_id      = aws_vpc.cert_vpc.id
  count = local.enable_CA_resources ? 1 : 0

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
  count = local.enable_CA_resources ? 1 : 0

  ingress {
    description = "connection to CA from lambda"
    from_port   = 9000
    to_port     = 9000
    protocol    = "tcp"
    security_groups = [aws_security_group.lambda_sg[0].id]
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
    sg_id     = aws_security_group.ca_sg[0].id
    region    = data.aws_region.current.name
  }
  count = local.enable_CA_resources ? 1 : 0

  provisioner "local-exec" {
    when       = destroy
    interpreter = ["python3", "-c"]
    command    = <<EOT
import sys, subprocess, json, time
region = "${self.triggers.region}"
subnet_id = "${self.triggers.subnet_id}"
result = subprocess.run(['aws', 'ec2', 'describe-network-interfaces', '--filters', f'Name=subnet-id,Values={subnet_id}', '--query', "NetworkInterfaces[?InterfaceType!='lambda'].NetworkInterfaceId", '--output', 'json', '--region', region], capture_output=True, text=True)
if result.returncode != 0:
    print("describe-network-interfaces function failed")
    print(result.stderr, file=sys.stderr)
    sys.exit(1)
enis = json.loads(result.stdout) if result.stdout.strip() else []
if not enis:
    print("No ENIs to delete")
    sys.exit(0)
failed = []
for eni in enis:
    deleted = False
    for attempt in range(40):
        r = subprocess.run(['aws', 'ec2', 'delete-network-interface', '--network-interface-id', eni, '--region', region], capture_output=True, text=True)
        if r.returncode == 0:
            deleted = True
            break
        if 'currently in use' in r.stderr:
            print(f'ENI {eni} in use, waiting...')
            time.sleep(15)
        else:
            print(f"Error caught while deleting {eni}: {r.stderr}", file=sys.stderr)
            break
    if not deleted:
        failed.append(eni)
if failed:
    print(f"Failed to delete the following ENIs: {failed}", file=sys.stderr)
    sys.exit(1)
print("ENI deletion successful")
EOT
  }

  depends_on = [aws_subnet.private_subnet, aws_security_group.ca_sg]
}

resource "aws_security_group" "vpce_sg" {
  name        = "${var.deploy_env}-vpce-sg"
  description = "connection for ssm endpoints"
  vpc_id      = aws_vpc.cert_vpc.id
  count = local.enable_CA_resources ? 1 : 0

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
    security_groups = [aws_security_group.ca_sg[0].id]
  }

  egress {
    from_port   = 0
    to_port     = 0
    protocol    = "-1"
    cidr_blocks = ["0.0.0.0/0"]
  }
}

locals {
  ssm_endpoints = local.enable_CA_resources ? {
    ssm        = "ssm"
    ssmmessages = "ssmmessages"
    ec2messages = "ec2messages"
  } : {}
}