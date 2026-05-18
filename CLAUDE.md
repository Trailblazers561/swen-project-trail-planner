# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## ⚠️ Environment Safety Rule — READ FIRST

**STRICTLY OFF LIMITS — do NOT modify, deploy to, or destroy resources in these environments:**
- **Legacy V1 production** (`default` workspace, no resource prefix) — `tusage.adirondackwilderness.org`. This is the V2 team's planned promotion target. CloudFront `E2PAASMSQFH9QT`, S3 bucket `trails.adirondackwilderness.org`, legacy API key `AWA-trail-counter-device-key-2016`. **Do not run `terraform destroy` while `default` workspace is selected.**
- **V2 environments** — `trailblazers-tst.adirondackwilderness.org`, `trailblazers-uat.adirondackwilderness.org`. V2 student team's territory.

**Safe / active environments (TrailCount cutover targets):**
- **`adk-test` workspace** — `test.adk.trailcount.io`, resources prefixed `tc-adk-test-`. Active dev for ADK promotions.
- **`adk-prod` workspace** — `adk.trailcount.io`, resources prefixed `tc-adk-prod-`. Real device data; The Garden trailhead deployment.
- **`demo-test` workspace** — `test.demo.trailcount.io`, resources prefixed `tc-demo-test-`. Craig's playground; full-volume synthetic traffic.
- **`demo-prod` workspace** — `demo.trailcount.io`, resources prefixed `tc-demo-prod-`. Public prospect-facing demo, ADK-flavored synthetic data.
- ~~**Legacy `tst` workspace**~~ — **destroyed 2026-05-18** (`terraform destroy -var-file=tst.tfvars` then `terraform workspace delete tst`). All 99 resources gone, including ~22K rows of simulated robot-counter test data. No longer in the workspace list.

**Always verify workspace before any plan/apply/destroy:** `terraform workspace show`.

## What This Repo Is

AWS backend + React frontend for the Adirondack trail counter system (adirondackwilderness.org). Physical trail counter devices detect hikers, batch events locally, and upload once daily to AWS. A React dashboard displays trail popularity as a line graph with selectable date range, granularity, trails, and wilderness area groups.

See the parent `CLAUDE.md` (at `trailcount/CLAUDE.md`) for full system context: hardware, firmware, SIM status, open issues, and the actual API endpoint/key the device uses.

## Branch Model — Read This First

**Active V1 branches — both wired into CI/CD as of 2026-05-18:**
- **`v1-develop`** — where v1.2.x work lands. Push triggers an auto-deploy to **adk-test + demo-test** via the GitHub Actions workflow at `.github/workflows/deploy.yml`.
- **`v1-prod`** — what's deployed to **adk-prod + demo-prod**. Push to this branch fires the prod deploy in CI. Promotion: `git checkout v1-prod && git merge v1-develop --ff-only && git push origin v1-prod`. The merge step is the deliberate human action; no manual approval gate inside CI yet.

**Historical / inactive V1 branches (do not work on):**
- `master` — student team work through April 2025; stale. Not in any CI trigger.
- `trailblazers-prod` — Cole's V1 extensions, deployed at `tusage.adirondackwilderness.org`. V2 team's planned promotion target. Not in any CI trigger.
- `v1.2` — vestigial alias at the same commit as `v1-prod` after 2026-05-18 FF. Not in any CI trigger. Will eventually be deleted or converted to a `v1.2.0` git tag; left in place for now.

**V2 branches (other team — do not work on):**
- `trailblazers-tst`, `trailblazers-uat`, etc. — V2 active development by Trailblazers team. The OIDC trust policy on the CI deploy role (`tc-github-actions-deploy`) is restricted to `v1-develop` + `v1-prod` only — workflows on `trailblazers-*` branches cannot assume the role even if a V2 dev pushed one. V2 will eventually migrate off `tusage.adirondackwilderness.org` to TrailCount infrastructure via their own change process; do not preempt this.

**DNS:** All DNS for `trailcount.io` and `adirondackwilderness.org` is managed via Squarespace, not Route 53 (Route 53 is empty in this account). ACM cert validation CNAMEs must be kept in Squarespace DNS or auto-renewal will fail.

**V2 migration handoff:** When V2 ships (~August 2026), the V1 device(s) deployed at The Garden continue uploading to `adk-prod` until V2 hardware replaces them (~December 2026). V2 webapp+backend retires V1's `adk-prod` stack at handoff. See `../CUTOVER_PLAN.md` and `../TERRAFORM_A2.md`.

## Commands

### React App (run from `swen-project-react-app/`)
```bash
npm install          # install deps
npm run dev          # dev server
npm run build        # production build → dist/
npm run lint         # ESLint
```

### Terraform (run from `terraform/`)

**AWS_PROFILE=trail-admin is required.** Terraform needs read permissions on DynamoDB / IAM / S3 that your `default` profile (`craigmcg` user) doesn't have. The `trail-admin` profile assumes the `Trail_Mgr_Adm` role and has what's needed. Symptom of forgetting: `AccessDenied` errors on `DescribeTable` / `GetRole` / `GetBucketPolicy` during plan refresh. See [[reference_aws_profiles]] in memory.

> ⚠️ **Always pass `-var-file=<workspace>.tfvars`** matching the current workspace. Bare invocation in a tenant-scoped workspace loads only `terraform.tfvars` (legacy prod values) and produces a destructive plan that wants to wipe the tenant stack. **Stop immediately if you see mass DynamoDB replacements or prefix-strip resource renames** — that's the missing-var-file signature.

```bash
# Active tenant-scoped workspaces (use these for ongoing work):
AWS_PROFILE=trail-admin terraform workspace select adk-test
AWS_PROFILE=trail-admin terraform plan  -var-file=adk-test.tfvars
AWS_PROFILE=trail-admin terraform apply -var-file=adk-test.tfvars     # creates ~50-100 resources

# Same pattern for adk-prod.tfvars, demo-test.tfvars, demo-prod.tfvars.

# Legacy default workspace (V2's planned target — OFF LIMITS, see Environment Safety Rule):
# Do not run terraform apply/destroy here.

terraform workspace show                          # always confirm workspace first
```

**Terraform state is remote (S3 + DynamoDB locking) as of 2026-05-18.** The `terraform/backend.tf` configures the S3 backend; running `terraform init` automatically points at `s3://tc-tfstate-650244845886/env/<workspace>/webapp/terraform.tfstate` with state-locking through DynamoDB table `tc-terraform-locks`. CI runners and local `terraform` runs share the same state. The `terraform.tfstate.d/` directory still exists locally with pre-migration backups (`*.pre-migrate-*.backup`) — kept for emergency rollback, gitignored.

#### First apply of a new tenant stack — the two-wave Squarespace DNS dance

When you first `terraform apply` against e.g. `adk-test`, the apply will **pause** at `aws_acm_certificate_validation` — waiting for the ACM certs to be DNS-validated. In a second terminal, run `terraform output -json` to retrieve `dashboard_cert_validation_records` and `api_cert_validation_records`. Add those CNAMEs to Squarespace's DNS for `trailcount.io`. ACM polls DNS, validates within ~5 min, apply resumes and creates CloudFront + API Gateway custom domain.

Once apply completes, retrieve `dashboard_cname_target` and `api_cname_target` outputs and add the user-facing CNAMEs in Squarespace:
- `var.dashboard_domain` (e.g. `test.adk.trailcount.io`) → `dashboard_cname_target` (a `*.cloudfront.net` host)
- `var.api_domain` (e.g. `api.test.adk.trailcount.io`) → `api_cname_target` (an `*.execute-api.us-east-1.amazonaws.com` regional host)

#### Retrieving the device API key for a tenant stack

For tenant-scoped workspaces, the device API key is auto-generated by `random_password` (see `terraform/secrets.tf`). After apply:

```bash
AWS_PROFILE=trail-admin terraform output -raw device_api_key
```

Paste the value into firmware `Core/Inc/secrets.h` (`DEVICE_API_KEY` macro), rebuild, and flash. Same firmware-side workflow as today; just changes where the value originates. To rotate: change a `keepers` argument on the `random_password` resource and re-apply.

### Tests
```bash
# API tests (from swen-project-react-app-API-tests/completed/) — Cole-era, manual-run
pytest completed/ -v        # requires BASE_URL, COGNITO_TOKEN, API_KEY in config.py

# UI tests — Selenium/Chrome (from swen-project-react-app-UI-tests/completed/) — Cole-era, manual-run
pytest completed/ -v        # requires BASE_URL, LOGIN_EMAIL, LOGIN_PASSWORD in config.py

# test_platform/ — Python scripts that simulate device uploads, seed/purge data,
# and validate the backend post-deploy. See test_platform/CLAUDE.md for usage.
# Requires TRAIL_API_KEY env var (and AWS_PROFILE=trail-admin for purge.py).
```

## CI/CD — GitHub Actions deploy workflow

`.github/workflows/deploy.yml` runs `terraform apply` against tenant workspaces in response to pushes on V1 branches:

| Push to | Auto-deploys to | Run topology |
|---|---|---|
| `v1-develop` | adk-test + demo-test | matrix job, two envs run in parallel |
| `v1-prod` | adk-prod + demo-prod | matrix job, two envs run in parallel |

Pushes to any other branch (master, trailblazers-*, feature branches) do **not** trigger this workflow. The `paths:` filter also skips runs when only docs change (READMEs, ISSUES.md, CLAUDE.md edits).

**AWS auth via OIDC, no long-lived secrets.** The workflow uses `aws-actions/configure-aws-credentials@v4` to exchange a GitHub-issued OIDC token for temporary AWS credentials. The IAM role is `tc-github-actions-deploy`; its trust policy is locked to two specific repo sub claims:
```
repo:Trailblazers561/swen-project-trail-planner:ref:refs/heads/v1-develop
repo:Trailblazers561/swen-project-trail-planner:ref:refs/heads/v1-prod
```
Workflows on any other ref (PR, trailblazers-*, master, feature branch) cannot assume the role. Known follow-up: scope the role's attached policy down from `AdministratorAccess` (see ISSUES.md / TODO list).

**State backend resources (created out-of-band via AWS CLI on 2026-05-18, not in terraform):**
- S3 bucket `tc-tfstate-650244845886` — terraform state for all four tenant workspaces (versioning + encryption + public-access-block enabled)
- DynamoDB table `tc-terraform-locks` — state locking (PAY_PER_REQUEST)
- IAM OIDC provider `token.actions.githubusercontent.com` — account-wide; shared infrastructure (V2 can use it later if they want their own CI)
- IAM role `tc-github-actions-deploy` — assumed by GitHub Actions; AdministratorAccess attached (scope-down pending)

Recreation steps if any of these are lost: see comments at the top of `terraform/backend.tf`.

**Manual workflow_dispatch** is also defined in the workflow file but not visible in the GitHub Actions UI (because the file isn't on the default branch — intentional, so V2's default-branch experience is unchanged). To trigger manually:
```bash
gh api repos/Trailblazers561/swen-project-trail-planner/actions/workflows/deploy.yml/dispatches \
  -f ref=v1-develop -f 'inputs[env]=adk-test'
```
Or just push to the relevant branch and let auto-deploy handle it.

## Lambda Architecture

All 11 Lambda functions live in a single file: `lambdas/traildata.py`. They are deployed as separate Lambda resources in Terraform (`terraform/lambdas.tf`).

| Handler | Method | Route | Notes |
|---------|--------|-------|-------|
| `get_trail_data` | GET | `/trail_data` | Filter by `trails=1,2,3`, `start`/`end` Unix timestamps; concurrent queries via ThreadPoolExecutor |
| `upload_trail_data` | POST | `/trail_data` | Cognito auth; batch writes to TrailDeviceLogs |
| `upload_device_data` | POST | `/devices` | **API key auth** (no Cognito); resolves `trail_id` from DeviceMetadata → recent log GSI → defaults to 0; filters timestamps before 2025-01-01; accepts empty `data` arrays (fixed — firmware no longer sends `{"ts":1}`); extracts `firmware_version`, `rssi`, `rsrp`, `rsrq`; writes to DeviceCallLog on every call-in |
| `get_trail_metadata` | GET | `/trail_metadata` | All trail names and IDs |
| `create_trail` | POST | `/trail_metadata` | Auto-increments `trail_id`; adds to "All Areas" group automatically |
| `update_trail_metadata` | PUT | `/trail_metadata` | Rename trail and/or change group membership |
| `delete_trail` | DELETE | `/trail_metadata` | Cascading: removes from groups, sets devices to trail_id=0, deletes all logs |
| `get_device_metadata` | GET | `/device_metadata` | Returns device_id, current_trail_id, battery, last_update |
| `update_device_trail_association` | PUT | `/device_metadata` | Associate a device with a trail |
| `get_trail_groups` | GET | `/trail_groups` | All groups with their trail_id lists |
| `get_device_call_log` | GET | `/device_call_log` | No params = most recent entry per device; `?device_id=xxx` = full history newest first |

## DynamoDB Tables (V1 / trailblazers-prod)

| Table | Partition key | Sort key | Notable fields |
|-------|--------------|----------|----------------|
| `TrailDeviceLogs` | `trail_id` (N) | `timestamp` (N) | `device_id`, `battery`; GSI: `device_id-timestamp-index` |
| `DeviceMetadata` | `device_id` (S) | — | `current_trail_id`, `battery`, `last_update` |
| `TrailMetadata` | `trail_id` (N) | — | `trail_name`; GSI: `trail_name-index` |
| `TrailGroups` | `group_name` (S) | — | `trail_ids` (list of numbers) |
| `DeviceCallLog` | `device_id` (S) | `timestamp` (N) | `firmware_version`, `battery`, `rssi`, `rsrp`, `rsrq`, `record_count`, `trail_id`; written on every call-in |

Trail IDs seeded by Terraform: Mt. Marcy (1), Wolf Creek Mountain (2), Mt. Joe (3), Mt. America (4), Blueberry Trail (5), Sunset Peak (6), Cedar Loop (7), Eagle Ridge (8), Bear Claw Path (9). Groups: All Areas (1–9), High Peaks (1,2), Giant Mountain (3,4), Five Ponds (5,6,7).

## Auth Model

- **React dashboard endpoints** — Cognito `USER_PASSWORD_AUTH`; ID token sent as `Authorization: Bearer <token>` from sessionStorage
- **`POST /devices`** — API key only (`X-API-Key` header), `authorization_type = NONE`; rate-limited: 50 req/s, 100 burst, 10k/day via API Gateway usage plan
- API key handling differs by workspace:
  - **Legacy `tst` / `default` workspaces**: key is set in `terraform.tfvars` / `tst.tfvars` (gitignored or committed-with-staging-value), and pasted into firmware `secrets.h` (gitignored). The old compromised key (`MSD-24572-TRAIL-PLANNER-KEY`) was rotated out.
  - **New tenant-scoped workspaces** (`adk-*`, `demo-*`): key is auto-generated by `random_password` in `secrets.tf`. Retrieve with `AWS_PROFILE=trail-admin terraform output -raw device_api_key` and paste into firmware `secrets.h`. Each tenant gets a unique key.

## React App Structure

`src/dashboard.tsx` is the main component. It has two views toggled by a button:
- **Graph view** — Plotly line charts with date range pickers, granularity selector (auto-adjusts: hourly/daily/weekly/monthly/yearly based on span), multi-select trail picker with area/group support
- **Device View** — Device-centric table sourced from DeviceCallLog (most recent entry per device). Columns: Device ID (clickable), Associated Trail, Weekly Count, Firmware, Battery, Last Call-in. Unassociated devices sort to top with an inline "Assign Trail" dropdown. Associated devices have a pencil (✎) edit button to reassign. Clicking a device ID opens `DeviceDetailModal` showing the last 5 call-ins with full telemetry.

Modals for trail management (create/edit/delete) and area/group management live in `src/components/`. The old `AssociateDeviceModal` has been removed — trail association is now handled inline in Device View.

API calls are centralized in `src/api.ts` — the `TrailData()` factory function returns methods for all endpoints, each injecting the Cognito token via `authHeaders()`.

## Generated Files (Do Not Edit)

Terraform writes these during `terraform apply`; they are gitignored:
- `swen-project-react-app/.env` — `VITE_API_URL`, `VITE_COGNITO_REGION`, `VITE_COGNITO_USER_POOL_ID`, `VITE_COGNITO_CLIENT_ID`

The React app reads Cognito IDs from these env vars at build time (see `src/cognito/authService.tsx` — `import.meta.env.VITE_COGNITO_*`). The old `src/cognito/config.json` file written by a now-deleted `local_sensitive_file.user_pool_config` resource was dead code (nothing imported it) and was removed 2026-05-18. **Do not re-add a `local_sensitive_file` that writes into `src/`** — it'll trigger a `fileset()` race in `null_resource.deploy_react_app` that breaks first-time CI deploys on fresh workspaces.

If the React app can't reach the API or Cognito, check `.env` exists and contains correct values from the deployed Terraform stack.

## Key Terraform Variables

`terraform/variables.tf`:

**Tenant-scoping (added in A2 of the cutover):**
- `tenant` — tenant name (e.g. `"adk"`, `"demo"`). Empty = legacy workspaces.
- `env` — env within a tenant (`"prod"`, `"test"`). For legacy: `""` (default workspace) or `"tst"` (legacy staging).
- `manage_dns` — bool, default false. When true, Terraform creates ACM certs + CloudFront with custom domain + API Gateway custom domain. New tenant-scoped workspaces set this true.
- `dashboard_domain` — full FQDN for the dashboard (e.g. `"adk.trailcount.io"`). Used only when `manage_dns = true`.
- `api_domain` — full FQDN for the API (e.g. `"api.adk.trailcount.io"`). Used only when `manage_dns = true`.

**Other:**
- `authorization_type` — `"COGNITO_USER_POOLS"` (default) or `"NONE"`
- `device_api_key` — used only by legacy workspaces (provide in tfvars). New tenant-scoped workspaces auto-generate via `random_password` in `secrets.tf`.

**Dead variables** (kept for legacy compatibility with the `default` workspace; can be removed once V2 promotes off the legacy stack):
- `has_cdn`, `has_domain`, `acm_certificate_arn` — replaced by `manage_dns` + auto-generated certs.

**Resource naming pattern:**
- New tenant-scoped: `tc-<tenant>-<env>-<resource>` (e.g. `tc-adk-test-DeviceMetadata`)
- Legacy staging: `tst-<resource>` (preserved)
- Legacy prod: no prefix (preserved; V2's promotion target)

**Terraform files of note:**
- `backend.tf` (added 2026-05-18) — S3 backend config + recreation instructions for the state-bucket / lock table if they're ever lost
- `acm.tf` — ACM cert resources (dashboard + api) gated by `manage_dns`
- `cloudfront.tf` — CloudFront distribution + OAC + bucket policy, gated by `manage_dns`
- `api_custom_domain.tf` — API Gateway custom domain + base path mapping, gated by `manage_dns`
- `secrets.tf` — `random_password` for device API key + the local that resolves it
- `outputs.tf` — DNS validation records, traffic CNAME targets, and `cloudfront_distribution_id` (used by CI for cache invalidation). All return null/empty for non-tenant workspaces.

Full API reference: `API_DOCUMENTATION.md` in the repo root.

The high-level cutover plan + Terraform refactor primer live in the parent project: `../CUTOVER_PLAN.md` and `../TERRAFORM_A2.md`.
