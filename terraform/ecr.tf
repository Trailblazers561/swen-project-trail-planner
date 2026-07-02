resource "aws_ecr_repository" "step_ca" {
  name                 = "${var.deploy_env}-step-ca"
  image_tag_mutability = "MUTABLE"
  force_delete         = true

  image_scanning_configuration {
    scan_on_push = true
  }

  tags = {
    Name = "${var.deploy_env}-step-ca"
  }
}

output "step_ca_ecr_url" {
  value = "${aws_ecr_repository.step_ca.repository_url}:${var.step_ca_version}"
}