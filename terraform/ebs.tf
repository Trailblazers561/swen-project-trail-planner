resource "aws_ebs_volume" "ca_data" {
  availability_zone = "${data.aws_region.current.name}a"
  size = 8
  encrypted = true
  tags = {
    Name = "${var.deploy_env}_ca_data"
  }
  count = local.enable_CA_resources ? 1 : 0
}

resource "aws_volume_attachment" "ca_data" {
  device_name = "/dev/sdf"
  volume_id = aws_ebs_volume.ca_data[0].id
  instance_id = aws_instance.ca_instance[0].id
  count = local.enable_CA_resources ? 1 : 0
}