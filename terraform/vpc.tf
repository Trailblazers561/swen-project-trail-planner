resource "aws_vpc" "cert_vpc" {
  cidr_block = "10.0.0.0/16"
  instance_tenancy = "default"
  enable_dns_support = "true"
  enable_dns_hostnames = "true"
  tags = {
    Name = "${var.deploy_env}_main_vpc"
  }
}

resource "aws_subnet" "public_subnet" {
  vpc_id = aws_vpc.cert_vpc.id
  cidr_block = "10.0.1.0/24"
  map_public_ip_on_launch = "true"
  availability_zone = "${data.aws_region.current.name}a"
  tags = {
    Name = "${var.deploy_env}_Public_Subnet"
  }
}

resource "aws_subnet" "private_subnet" {
  vpc_id = aws_vpc.cert_vpc.id
  cidr_block = "10.0.4.0/24"
  map_public_ip_on_launch = "false"
  availability_zone = "${data.aws_region.current.name}a"
  tags = {
    Name = "${var.deploy_env}_Private_Subnet"
  }
}

resource "aws_internet_gateway" "IGW" {
  vpc_id = aws_vpc.cert_vpc.id
  tags = {
    Name = "${var.deploy_env}_IGW"
  }
}

resource "aws_route_table" "public_RT" {
  vpc_id = aws_vpc.cert_vpc.id

  route {
    cidr_block = "0.0.0.0/0"
    gateway_id = aws_internet_gateway.IGW.id
  }

  tags = {
    Name = "${var.deploy_env}_Public_RT"
  }
}

resource "aws_route_table_association" "public_subnet_1" {
  subnet_id = aws_subnet.public_subnet.id
  route_table_id = aws_route_table.public_RT.id
}

resource "aws_route_table" "private_RT" {
  vpc_id = aws_vpc.cert_vpc.id

  tags = {
    Name = "${var.deploy_env}_Private_RT"
  }
}

resource "aws_route_table_association" "private_subnet_1" {
  subnet_id = aws_subnet.private_subnet.id
  route_table_id = aws_route_table.private_RT.id
}

resource "aws_vpc_endpoint" "dynamodb" {
  vpc_id            = aws_vpc.cert_vpc.id
  service_name      = "com.amazonaws.${data.aws_region.current.name}.dynamodb"
  vpc_endpoint_type = "Gateway"
  route_table_ids = [aws_route_table.private_RT.id]
  depends_on = [null_resource.nuke_enis]
  count = local.enable_CA_resources ? 1 : 0

  tags = {
    Name = "${var.deploy_env}_dynamodb_endpoint"
  }
}

resource "aws_vpc_endpoint" "secretsmanager" {
  vpc_id              = aws_vpc.cert_vpc.id
  service_name        = "com.amazonaws.${data.aws_region.current.name}.secretsmanager"
  vpc_endpoint_type   = "Interface"
  subnet_ids          = [aws_subnet.private_subnet.id]
  security_group_ids  = [aws_security_group.lambda_sg[0].id, aws_security_group.vpce_sg[0].id, aws_security_group.ca_sg[0].id]
  private_dns_enabled = true
  depends_on = [null_resource.nuke_enis]
  count = local.enable_CA_resources ? 1 : 0

  tags = {
    Name = "${var.deploy_env}_secretsmanager_endpoint"
  }
}

resource "aws_vpc_endpoint" "s3" {
  vpc_id            = aws_vpc.cert_vpc.id
  service_name      = "com.amazonaws.${data.aws_region.current.name}.s3"
  vpc_endpoint_type = "Gateway"
  route_table_ids   = [aws_route_table.private_RT.id]
  depends_on = [null_resource.nuke_enis]
  count = local.enable_CA_resources ? 1 : 0

  tags = {
    Name = "${var.deploy_env}_s3_endpoint"
  }
}

resource "aws_vpc_endpoint" "ssm" {
  for_each            = local.ssm_endpoints
  vpc_id              = aws_vpc.cert_vpc.id
  service_name        = "com.amazonaws.${data.aws_region.current.name}.${each.value}"
  vpc_endpoint_type   = "Interface"
  subnet_ids          = [aws_subnet.private_subnet.id]
  security_group_ids  = [aws_security_group.vpce_sg[0].id]
  private_dns_enabled = true
  depends_on = [null_resource.nuke_enis]

  tags = {
    Name = "${var.deploy_env}_${each.value}_endpoint"
  }
}

resource "aws_vpc_endpoint" "ecr_api" {
  vpc_id              = aws_vpc.cert_vpc.id
  service_name        = "com.amazonaws.${data.aws_region.current.name}.ecr.api"
  vpc_endpoint_type   = "Interface"
  subnet_ids          = [aws_subnet.private_subnet.id]
  security_group_ids  = [aws_security_group.vpce_sg[0].id]
  private_dns_enabled = true
  depends_on = [null_resource.nuke_enis]
  count = local.enable_CA_resources ? 1 : 0

  tags = {
    Name = "${var.deploy_env}_ecr_api_endpoint"
  }
}

resource "aws_vpc_endpoint" "ecr_dkr" {
  vpc_id              = aws_vpc.cert_vpc.id
  service_name        = "com.amazonaws.${data.aws_region.current.name}.ecr.dkr"
  vpc_endpoint_type   = "Interface"
  subnet_ids          = [aws_subnet.private_subnet.id]
  security_group_ids  = [aws_security_group.vpce_sg[0].id]
  private_dns_enabled = true
  depends_on = [null_resource.nuke_enis]
  count = local.enable_CA_resources ? 1 : 0

  tags = {
    Name = "${var.deploy_env}_ecr_dkr_endpoint"
  }
}