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

resource "null_resource" "push_step_ca_image" {
  triggers = {
    ecr_repo        = aws_ecr_repository.step_ca.repository_url
    step_ca_version = var.step_ca_version
  }

  provisioner "local-exec" {
    interpreter = ["python", "-c"]
    command     = <<-EOT
import subprocess, sys
region = "${data.aws_region.current.name}"
account_id = "${aws_ecr_repository.step_ca.registry_id}"
repo_url = "${aws_ecr_repository.step_ca.repository_url}"
version = "${var.step_ca_version}"
registry = f"{account_id}.dkr.ecr.{region}.amazonaws.com"
def run(cmd, input=None):
  result = subprocess.run(cmd, input=input, capture_output=True, text=True)
  if result.returncode != 0:
    print(result.stderr)
    sys.exit(result.returncode)
  return result.stdout
run(["aws", "ecr", "get-login-password", "--region", region], input=None)
password = run(["aws", "ecr", "get-login-password", "--region", region])
run(["docker", "login", "--username", "AWS", "--password-stdin", registry], input=password)
run(["docker", "pull", f"smallstep/step-ca:{version}"])
run(["docker", "tag", f"smallstep/step-ca:{version}", f"{repo_url}:{version}"])
run(["docker", "push", f"{repo_url}:{version}"])
EOT
  }

  depends_on = [aws_ecr_repository.step_ca]
}

output "step_ca_ecr_url" {
  value = "${aws_ecr_repository.step_ca.repository_url}:${var.step_ca_version}"
}