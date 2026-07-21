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

resource "null_resource" "push_step_ca" {
  count = local.enable_CA_resources && local.local_run ? 1 : 0

  provisioner "local-exec" {
    command = "python3 ../scripts/push_step_ca.py ${var.deploy_env} ${var.step_ca_version}"
  }

  depends_on = [ aws_ecr_repository.step_ca ]
}