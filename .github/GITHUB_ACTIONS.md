# Github Actions Overview

Github actions can be used to automatically do different things based off predefined triggers in the website. In this case, it is used to run tests when making pull requests, and to automatically keep environments deployed with the latest code. More information on github actions can be found in the Github Actions Guide [Testing Guidebook](https://docs.google.com/document/d/1MuMDhpsaSYin0_dwiCYS0pto_3ukT58MzCKLO7v9ang/edit?tab=t.0) 
<span style="color: red;font-size: 50pt;font-family: Comic Sans MS;"> UPDATE THIS TO INTERNAL LINK </span>

## Github Action Parts

### Name
```name:```

This is at the start of an action and is the name that will appear after the slash when viewing the run

### Triggers
```on:```

This is where the trigger for the action is defined. This can be pull_request, push, issue_comment, status, etc. For a full list of trigger events look [here](https://docs.github.com/en/actions/reference/workflows-and-actions/events-that-trigger-workflows). Trigger events can have types, create, edit, delete, etc. and filters, branches, tags, etc. That further limit when the action is called.

### Env
```env:```

This is where you can specify enviornment variables that can be used throughout the action. These can be hardcoded in the action, or reference variables defined in the repository secrets. Terraform variables can also be redefined in this way, more information on those in the [terraform section](#terraform)

### Jobs
```jobs:```

Actions are seperated into various jobs that get run parallel to each other. All actions in this repository only have one job. Each job has different fields, an `id`, `name`, `runs-on`, `permissions`, `environment`, and `env`. The `id` is whatever the section directly under `jobs` is called, rather than something explicitly stated with `id:`. The `name` is the first part of what the job will be called when viewing it. The `runs-on` is the runner for the specific job, with all jobs in this repository running on _ubuntu-latest_. `permissions` is what the action has access to within the github api. `environment` specifies a github environment to use, more in the [environments and secrets section](#environments-and-secrets). `env` is where environment variables are defined specific to the job.

### Steps
```steps:```

Steps are the proccesses that make up a given job. They run in the order they are specified with fields `name`, `uses`, `id`, `run`, `with`, and `if`. `name` is what the step will be called when viewing it. `uses` is a way to link the step to call a premade action that the step will call. `id` is an id that can be used in other steps to reference a specific step. `run`is used to run one or more shell commands, with `|` indicating to run multiple commands in sequence. `with` is used to pass parameters to the given step, often used in combination with `uses`. `if` specifies a condition on when to run the step, by default being to run if none of the previous steps had an error.

### Scripts

You can run javascript code in the action by creating a step and settting `uses: actions/github-script@v6` and passing `with:` with parameters `github-token:` and `script:` to run the provided script.

### Environments and Secrets

Github repositories can have environments that specify variables, either public or secret, that can be referenced within a given action. Secrets can be tied to a specific environment, or for the entire repository. Environment variables can be referenced by using `${{ vars.VARIABLE_NAME }}` and secrets by using `${{ secrets.VARIABLE_NAME }}`

### Terraform

HasiCorp (terraform's company) have setup a way to create a terraform workspace that can manage terraform resources for you. This workspace can be updated using github actions to automatically create and update aws resources on the cloud. Terraform variables can also be changed in the github action by defining a variable in the `env:` with the format `TF_VAR_<variable-name>`.

## Specific Actions

### Terraform Plan

This action runs when a pull request is created or updated for one of three branches, trailblazers-tst, trailbazers-uat, and trailblazers-prod. It will run a terraform plan going from the current configuration to the proposed configuration, and ensure that the new react code successfully builds. It will then output the results, success or failure, in a comment on the pull request. This action will _fail_ if it doesn't successfully plan or build, and _pass_ if everything work properly. The _pass_/_fail_ results of this action will be displayed on the pull request that triggered them.

### Terraform Apply

This action runs when code is pushed for one of three branches, trailblazers-tst, trailbazers-uat, and trailblazers-prod. It will run terraform apply using the new code to update the workspace to the latest version. It then updates the react bucket with the latest files by building the react files and syncing the bucket contents to the new build.

### Integration Testing

This action runs when a pull request is created or updated for one of three branches, trailblazers-tst, trailbazers-uat, and trailblazers-prod. It will create a new _test_ environment with the proposed changes, run all of the tests against that enviornment, output the results in a comment and attach `test-results.xml`, and destroy the test environment. This action will _fail_ if any of the creation/deletion fails, or if any tests fail, and _pass_ if everything works properly with all tests passing. The _pass_/_fail_ results of this action will be displayed on the pull request that triggered them.