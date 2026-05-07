# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## What This Repo Is

AWS backend + React frontend for the Adirondack trail counter system (adirondackwilderness.org). Physical trail counter devices detect hikers, batch events locally, and upload once daily to AWS. A React dashboard displays trail popularity as a line graph with selectable date range, granularity, trails, and wilderness area groups.

See the parent `CLAUDE.md` (at `trail_counter_v1/CLAUDE.md`) for full system context: hardware, firmware, SIM status, open issues, and the actual API endpoint/key the device uses.

## Branch Model — Read This First

**`master` is stale** (student team work through April 2025). The live production deployment is on **`trailblazers-prod`** — Cole's extended version, serving `tusage.adirondackwilderness.org`. This branch is ~18 commits ahead with a largely rewritten Lambda and new DynamoDB tables.

**`v1.2` is the active development branch** (Craig, 2026-05-07). Branched from `trailblazers-prod`. Contains Phase 3 backend fixes: timestamp filtering, DynamoDB pagination, metadata endpoint pagination, error display in dashboard, default start date/granularity improvements, and Terraform deploy reliability fixes. Deployed to staging; pending production promotion.

Note: `trails.adirondackwilderness.org` does not resolve — the live frontend URL is `tusage.adirondackwilderness.org` (CloudFront distribution `E2PAASMSQFH9QT`). DNS for adirondackwilderness.org is managed via Squarespace, not Route53 (Route53 is empty in this account). ACM cert validation CNAMEs must be kept in Squarespace DNS or auto-renewal will fail.

**V2 is in active development** on `trailblazers-*` branches (Trailblazers team). Do not touch those branches or their deployed environments:
- `trailblazers-tst.adirondackwilderness.org` — V2 test
- `trailblazers-uat.adirondackwilderness.org` — V2 UAT

All V1 work uses `v1.2` (branched from `trailblazers-prod`). When promoting to production, merge `v1.2` → `trailblazers-prod`.

**V2 migration — preferred path:** Deploy an adapter on the current V1 endpoint (`POST /trailplanner_api_stage/devices`) that accepts V1-format payloads. The V1 trail counter will be physically deployed at The Garden trailhead (Keene Valley, NY) ~May 18, 2026 for the summer. An adapter means the device can stay in place when V2 goes live — no field visit needed. The device endpoint can be updated via `config.txt` without reflashing, but the API key cannot.

## Commands

### React App (run from `swen-project-react-app/`)
```bash
npm install          # install deps
npm run dev          # dev server
npm run build        # production build → dist/
npm run lint         # ESLint
```

### Terraform (run from `terraform/`)
```bash
terraform init       # first-time setup
terraform plan       # preview changes
terraform apply      # deploy (also builds and syncs React app to S3)
terraform destroy    # tear down all AWS resources
```

### Tests
```bash
# API tests (from swen-project-react-app-API-tests/completed/)
pytest completed/ -v        # requires BASE_URL, COGNITO_TOKEN, API_KEY in config.py

# UI tests — Selenium/Chrome (from swen-project-react-app-UI-tests/completed/)
pytest completed/ -v        # requires BASE_URL, LOGIN_EMAIL, LOGIN_PASSWORD in config.py
```

## Lambda Architecture

All 10 Lambda functions live in a single file: `lambdas/traildata.py`. They are deployed as separate Lambda resources in Terraform (`terraform/lambdas.tf`).

| Handler | Method | Route | Notes |
|---------|--------|-------|-------|
| `get_trail_data` | GET | `/trail_data` | Filter by `trails=1,2,3`, `start`/`end` Unix timestamps; concurrent queries via ThreadPoolExecutor |
| `upload_trail_data` | POST | `/trail_data` | Cognito auth; batch writes to TrailDeviceLogs |
| `upload_device_data` | POST | `/devices` | **API key auth** (no Cognito); resolves `trail_id` from DeviceMetadata → recent log GSI → defaults to 0; filters timestamps before 2025-01-01 |
| `get_trail_metadata` | GET | `/trail_metadata` | All trail names and IDs |
| `create_trail` | POST | `/trail_metadata` | Auto-increments `trail_id`; adds to "All Areas" group automatically |
| `update_trail_metadata` | PUT | `/trail_metadata` | Rename trail and/or change group membership |
| `delete_trail` | DELETE | `/trail_metadata` | Cascading: removes from groups, sets devices to trail_id=0, deletes all logs |
| `get_device_metadata` | GET | `/device_metadata` | Returns device_id, current_trail_id, battery, last_update |
| `update_device_trail_association` | PUT | `/device_metadata` | Associate a device with a trail |
| `get_trail_groups` | GET | `/trail_groups` | All groups with their trail_id lists |

## DynamoDB Tables (V1 / trailblazers-prod)

| Table | Partition key | Sort key | Notable fields |
|-------|--------------|----------|----------------|
| `TrailDeviceLogs` | `trail_id` (N) | `timestamp` (N) | `device_id`, `battery`; GSI: `device_id-timestamp-index` |
| `DeviceMetadata` | `device_id` (S) | — | `current_trail_id`, `battery`, `last_update` |
| `TrailMetadata` | `trail_id` (N) | — | `trail_name`; GSI: `trail_name-index` |
| `TrailGroups` | `group_name` (S) | — | `trail_ids` (list of numbers) |

Trail IDs seeded by Terraform: Mt. Marcy (1), Wolf Creek Mountain (2), Mt. Joe (3), Mt. America (4), Blueberry Trail (5), Sunset Peak (6), Cedar Loop (7), Eagle Ridge (8), Bear Claw Path (9). Groups: All Areas (1–9), High Peaks (1,2), Giant Mountain (3,4), Five Ponds (5,6,7).

## Auth Model

- **React dashboard endpoints** — Cognito `USER_PASSWORD_AUTH`; ID token sent as `Authorization: Bearer <token>` from sessionStorage
- **`POST /devices`** — API key only (`X-API-Key` header), `authorization_type = NONE`; rate-limited: 50 req/s, 100 burst, 10k/day via API Gateway usage plan
- The current hardcoded API key (`MSD-24572-TRAIL-PLANNER-KEY`) was compromised; rotation is an open issue

## React App Structure

`src/dashboard.tsx` (954 lines) is the main component. It has two views toggled by a button:
- **Graph view** — Plotly line charts with date range pickers, granularity selector (auto-adjusts: hourly/daily/weekly/monthly/yearly based on span), multi-select trail picker with group support
- **List view** — Table of trail name, weekly count, battery (color-coded green/yellow/red), last updated date

Modals for trail management (create/edit/delete), group management, and device-to-trail association all live in `src/components/`.

API calls are centralized in `src/api.ts` — the `TrailData()` factory function returns methods for all endpoints, each injecting the Cognito token via `authHeaders()`.

## Generated Files (Do Not Edit)

Terraform writes these during `terraform apply`; they are gitignored:
- `swen-project-react-app/.env` — `VITE_API_URL`, `VITE_COGNITO_REGION`, `VITE_COGNITO_USER_POOL_ID`, `VITE_COGNITO_CLIENT_ID`
- `swen-project-react-app/src/cognito/config.json` — Cognito pool/client IDs

If the React app can't reach the API or Cognito, check these files exist and contain correct values from the deployed Terraform stack.

## Key Terraform Variables

`terraform/variables.tf`:
- `authorization_type` — `"COGNITO_USER_POOLS"` (default) or `"NONE"`
- `has_cdn` / `has_domain` — CloudFront and Route53 are opt-in (both default false)
- `acm_certificate_arn` — required when using a custom domain with CloudFront

Full API reference: `API_DOCUMENTATION.md` in the repo root.
