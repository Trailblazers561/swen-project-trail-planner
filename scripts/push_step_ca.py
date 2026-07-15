import boto3
import time
import subprocess
import sys
import os
print("Starting push step ca")
region = os.environ.get("AWS_DEFAULT_REGION", "us-east-1")
ecr = boto3.client('ecr', region_name=region)
sts = boto3.client('sts', region_name=region)
deploy_env = sys.argv[1]
step_ca_version = sys.argv[2]
repo_name = f"{deploy_env}-step-ca"

account_id = sts.get_caller_identity()['Account']
repo_url = f"{account_id}.dkr.ecr.{region}.amazonaws.com/{repo_name}"
registry = f"{account_id}.dkr.ecr.{region}.amazonaws.com"

try:
    while True:
        try:
            response = ecr.describe_repositories(repositoryNames=[repo_name])
            print("ECR ready to go, pushing stepCA")
            break
        except ecr.exceptions.RepositoryNotFoundException:
            print("No ECR found yet, waiting for 30s")
            time.sleep(30)

    password = subprocess.run(
        ["aws", "ecr", "get-login-password", "--region", region],
        capture_output=True, text=True, check=True
    ).stdout.strip()

    subprocess.run(
        ["docker", "login", "--username", "AWS", "--password-stdin", registry],
        input=password, text=True, check=True
    )

    subprocess.run(["docker", "pull", f"smallstep/step-ca:{step_ca_version}"], check=True)
    subprocess.run(["docker", "tag", f"smallstep/step-ca:{step_ca_version}", f"{repo_url}:{step_ca_version}"],
                   check=True)
    subprocess.run(["docker", "push", f"{repo_url}:{step_ca_version}"], check=True)

    print(f"StepCA push to {repo_url}:{step_ca_version} successful")
    with open("/tmp/ecr_done", "w") as f:
        f.write("success")

except Exception as e:
    with open("/tmp/ecr_done", "w") as f:
        f.write(f"error: {e}")
    sys.exit(1)