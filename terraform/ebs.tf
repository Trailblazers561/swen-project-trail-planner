resource "aws_ebs_volume" "ca_data" {
  availability_zone = "${data.aws_region.current.name}a"
  size = 8
  encrypted = true
  tags = {
    Name = "${var.deploy_env}_ca_data"
  }
}

resource "aws_volume_attachment" "ca_data" {
  device_name = "/dev/sdf"
  volume_id = aws_ebs_volume.ca_data.id
  instance_id = aws_instance.ca_instance.id
}