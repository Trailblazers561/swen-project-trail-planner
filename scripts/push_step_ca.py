import boto3
import time

ecr = boto3.client('ecr')
sts = boto3.client('sts')
deploy_env = sys.argv[1]
repo_name = f"{deploy_env}-step-ca"

account_id = sts.get_caller_identity()['Account']
repo_url = f"{account_id}.dkr.ecr.{region}.amazonaws.com/{repo_name}"
registry = f"{account_id}.dkr.ecr.{region}.amazonaws.com"

while True:
    try:
        response = ecr.describe_repositories(repositoryNames=[repo_name])
        print("ECR ready to go, pushing stepCA")
        break
    except ecr.exceptions.ResourceNotFoundException:
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

subprocess.run(["docker", "pull", "smallstep/step-ca:latest"], check=True)
subprocess.run(["docker", "tag", f"{repo_url}:latest"], check=True)
subprocess.run(["docker", "push", f"{repo_url}:latest"], check=True)

print(f"StepCA push to {repo_url}:latest successful")