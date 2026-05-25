# Changelog

## v1.2 (2026-05-08) — branch: v1.2

Work by Craig McGowan, branched from `trailblazers-prod`. Deployed to staging; pending production promotion.

### Device Health & Telemetry

- **DeviceCallLog DynamoDB table** — New table written on every device call-in (`POST /devices`). Captures `firmware_version`, `battery`, `rssi`, `rsrp`, `rsrq`, `record_count`, `trail_id`, and `timestamp` per upload. Provides a complete health history per device, independent of trail log data.
- **`GET /device_call_log` endpoint** — New Lambda + API Gateway route. No params returns most recent entry per device (used by Device View). `?device_id=xxx` returns full history for one device, newest first (used by detail modal).
- **`firmware_version` in upload payload** — `POST /devices` now accepts and stores `firmware_version` from the device payload. Firmware sends `"firmware_version": "1.1.0"` (defined as `#define FIRMWARE_VERSION` in `version.h`).
- **Empty `data` array accepted** — Lambda no longer rejects `POST /devices` with an empty `data` array (was returning 400). Firmware no longer needs to send a fake `{"ts": 1}` entry when there are no timestamps to report. Both sides of this two-bug cancellation are now fixed.

### Dashboard — Device View

- **Device View** (formerly "List View / Switch to List View") — Rebuilt as a device-centric table sourced from `DeviceCallLog` rather than from the trail list. Rows represent devices that have called in, not trails. Columns: Device ID, Associated Trail, Weekly Count, Firmware, Battery, Last Call-in.
- **Unassociated devices at top** — Devices with no trail association sort above associated devices. Devices in `DeviceMetadata` that have never called in also appear if unassociated.
- **Inline trail association** — "Associate Device" modal removed. Unassociated devices show an "Assign Trail" button inline. Associated devices show a pencil (✎) button to reassign. Both open a dropdown + Save/Cancel in the same row — no modal needed.
- **Inline unassociation** — When editing an associated device's trail, an "Unassign" button (red, next to Save) sets `trail_id=0` directly without requiring a dropdown selection.
- **Duplicate assignment prevention** — Trail assignment dropdown only lists trails not already assigned to another device, preventing two devices from being pointed at the same trail.
- **Device filter** — Search input above the device table filters rows by device ID as you type; handles large device lists without pagination.
- **Device detail modal** — Clicking a device ID opens a modal showing the last 5 call-ins for that device with full telemetry: date/time, firmware version, battery, RSSI, RSRP, RSRQ, and count.
- **Terminology** — "Switch to List View" → "Device View" button. "Trail Status Overview" → "Device Status Overview" heading. "Add Group" / "Edit Group" → "Add Area" / "Edit Area". Modal labels updated throughout: "Group Name" → "Area Name", "In group" / "Not in group" → "In area" / "Not in area". "Records" → "Count" in the detail modal.
- **Auto-select "All Trails" on login** — Trail selector now auto-selects "All Trails" on first data load instead of leaving the selection empty.

### Backend Scaling Fixes (Phase 3)

- **Timestamp filtering** — `get_trail_data()` now applies `start`/`end` as a `KeyConditionExpression`. Previously fetched all records for a trail and filtered in Python, hitting the Lambda 6 MB response limit at modest data volumes.
- **DynamoDB pagination** — All Lambda functions now loop on `LastEvaluatedKey`. Previously silently truncated results at DynamoDB's 1 MB page limit (~6,700 records). Affects `get_trail_data`, `get_trail_metadata`, `get_device_metadata`, `get_trail_groups`.
- **Lambda timeout** — All 11 Lambda functions set to 30s in Terraform (was 3s default, causing silent timeouts on larger queries).
- **User-visible fetch errors** — Dashboard displays a red error banner when a trail data fetch fails instead of silently showing an empty chart.
- **`source_code_hash` on Lambda resources** — Terraform now detects Lambda code changes and redeploys automatically on `terraform apply`.
- **React deploy trigger** — `null_resource.deploy_react_app` now uses a content hash trigger so `terraform apply` rebuilds and syncs the frontend whenever source files change.

### Dashboard — Graph View

- **Default start date** — Changed from hardcoded 2025-01-01 to January 1 of the current year.
- **Default granularity** — Changed from Daily to Weekly.
- **Aggregate toggle** — Combines all selected trails into a single summed line for easier total-traffic comparison.
- **Loading spinner** — Shown while chart data is fetching.
- **Area name in chart title** — When a wilderness area group is selected, the group name appears in the chart title.
- **401/403 redirect** — Dashboard redirects to `/login?reason=session_expired` on auth failure instead of silently failing.

### Infrastructure

- **Staging environment** — Terraform `env` variable prefixes all resource names (`tst-TrailDeviceLogs`, `tst-traildata_*`, etc.). Workspace `tst` holds isolated state. Deploy: `AWS_PROFILE=trail-admin terraform apply -var-file=tst.tfvars -auto-approve`.
- **Sensitive API key variable** — Device API key moved from hardcoded Terraform string to a `sensitive` variable in `terraform.tfvars` (gitignored). Staging uses a separate key in `tst.tfvars`.
- **Terraform seed data removed** — `aws_dynamodb_table_item` resources removed from `dynamodb.tf`. They were recreating deleted items on every `terraform apply`. Trail names and groups are now managed through the dashboard UI only.

### Security

- **API key rotation** — Old device API key (`MSD-24572-TRAIL-PLANNER-KEY`) was leaked to GitHub and has been rotated. New key is in `terraform/terraform.tfvars` (gitignored) and firmware `secrets.h` (gitignored).

---

## trailblazers-prod (2025–2026) — Trailblazers team

Extended and largely rewrote the original student backend. This is the live production branch serving `tusage.adirondackwilderness.org`.

- Rewrote Lambda functions into a single `traildata.py` with separate handlers per route
- Added `DeviceMetadata`, `TrailMetadata`, `TrailGroups` tables (original had one combined table)
- Added trail group / wilderness area support with `GET`/`POST`/`PUT`/`DELETE /trail_groups`
- Added trail management endpoints (`POST`, `PUT`, `DELETE /trail_metadata`) with cascading delete
- Added device-to-trail association (`PUT /device_metadata`)
- React dashboard: trail selector with group support, Plotly charts, modals for trail/group management, device association modal
- Cognito auth for all dashboard endpoints; API key auth for `POST /devices`
- Terraform: CloudFront + custom domain support, Cognito user pool, API key usage plan with rate limiting

---

## v1.0 / master (through April 2025) — Original student team (SWEN 261)

Initial implementation.

- Single Lambda, single DynamoDB table (`TrailDeviceLogs`)
- `POST /devices` — device data upload with API key auth
- `GET /trail_data` — query trail logs by trail ID and date range
- Basic React dashboard with Plotly line chart
- Terraform for API Gateway, Lambda, DynamoDB, S3, CloudFront
