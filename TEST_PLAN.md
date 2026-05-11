# Trail Counter System — Test Plan

References existing test suites and identifies gaps. Requirements are tracked in `USER_STORIES.md` and `ISSUES.md`.

---

## Test Strategy

### Test Levels

| Level | Tool | Location | Purpose |
|---|---|---|---|
| **API / Integration** | pytest + requests | `swen-project-react-app-API-tests/` | Verify every endpoint accepts correct input, returns correct output, and enforces auth |
| **UI / End-to-End** | pytest + Selenium | `swen-project-react-app-UI-tests/` | Verify the frontend renders and responds correctly for a logged-in user |
| **Performance / Scale** | `test_platform/` | `test_platform/` | Verify system behavior under realistic and boundary data volumes |
| **Smoke (post-deploy)** | `test_platform/` | `test_platform/` | Fast pass/fail check after any backend deployment |
| **Firmware** | Manual / hardware | On-device | Verify detection, buffering, and upload behavior with real hardware |

### Test Data Strategy
- API and UI tests operate against the **live deployed environment** (`tusage.adirondackwilderness.org` / `yb930th90j` API)
- `test_platform/` uses device ID prefix `test-` for records it creates, so they can be identified and purged without affecting nightly simulation data
- Tests that create data SHALL clean up after themselves (purge test records on pass or fail)
- Performance tests use `test_platform/populate.py` to seed controlled volumes before running

### Configuration
Both test suites require values in their `config.py` before running:
- `BASE_URL` — API Gateway URL or frontend URL
- `COGNITO_TOKEN` — valid JWT (expires; must be refreshed periodically)
- `API_KEY` — device upload API key (from `secrets.h`, never commit)

---

## Requirements Coverage Matrix

### Authentication & Authorization

| Requirement | Test Case | Type | File | Status |
|---|---|---|---|---|
| REQ-AUTH-1: Login required for data/metadata | `test_Login_Logout` | UI | `test_LoginLogout.py` | ✅ Exists |
| REQ-AUTH-1: Unauthenticated GET /trail_data returns 401 | `test_unauthorized_trail_data_access` | API | — | ❌ Gap |
| REQ-AUTH-2: /devices accepts API key, no Cognito | `test_post_device_data_success` | API | `test_DevicesPost.py` | ✅ Exists |
| REQ-AUTH-2: /devices rejects missing API key | `test_post_device_data_no_api_key` | API | `test_DevicesPostValidation.py` | ✅ Exists (verify) |
| REQ-AUTH-3: Rate limiting enforced on /devices | `test_rate_limit_devices` | API | — | ❌ Gap |
| REQ-AUTH-4: All authenticated users see all trails | Covered by general data access tests | API/UI | Multiple | ✅ Implicit |
| REQ-AUTH-5: User registration flow | `test_user_registration` | UI | — | ❌ Gap |

---

### Trail Management

| Requirement | Test Case | Type | File | Status |
|---|---|---|---|---|
| REQ-TRAIL-1: Trails have unique ID and name | `test_create_trail` | API | `test_TrailCreate.py` | ✅ Exists |
| REQ-TRAIL-2: Create trail assigns unique ID | `test_create_trail` | API | `test_TrailCreate.py` | ✅ Exists |
| REQ-TRAIL-2: Create trail via UI | `test_trail_modals` | UI | `test_TrailModals.py` | ✅ Exists |
| REQ-TRAIL-3: Rename trail | `test_update_trail_metadata` | API | `test_TrailMetadataUpdate.py` | ✅ Exists |
| REQ-TRAIL-4: Delete trail removes logs | `test_delete_trail_cascades_logs` | API | `test_TrailDelete.py` | ✅ Exists (verify cascade) |
| REQ-TRAIL-4: Delete trail removes group membership | `test_delete_trail_cascades_groups` | API | `test_TrailDelete.py` | ✅ Exists (verify) |
| REQ-TRAIL-4: Delete trail unpairs devices | `test_delete_trail_unpairs_devices` | API | — | ❌ Gap |
| REQ-TRAIL-5: Trails belong to wilderness group | `test_wilderness_groups` | UI | `test_WildernessGroups.py` | ✅ Exists |
| REQ-TRAIL-6: "All Areas" always exists and contains all trails | `test_all_areas_group` | API | `test_TrailGroupsGet.py` | ✅ Exists (verify) |
| REQ-TRAIL-7: Create/rename/delete custom groups | `test_trail_group_modals` | UI | `test_TrailGroupModals.py` | ✅ Exists |
| REQ-TRAIL-7: Add/remove trail from group | `test_update_trail_group_membership` | API | `test_TrailMetadataUpdate.py` | ✅ Exists (verify) |

---

### Device Management

| Requirement | Test Case | Type | File | Status |
|---|---|---|---|---|
| REQ-DEV-2: New device auto-registers as unpaired (trail_id=0) | `test_device_default_trail_id` | API | `test_DeviceDefaultTrailId.py` | ✅ Exists |
| REQ-DEV-3: Associate device to trail | `test_device_trail_association` | API | `test_DeviceTrailAssociation.py` | ✅ Exists |
| REQ-DEV-3: Reassign device to different trail | `test_device_reassignment` | API | — | ❌ Gap |
| REQ-DEV-4: Device battery and last-update shown | `test_device_metadata_get` | API | `test_DeviceMetadataGet.py` | ✅ Exists |
| REQ-DEV-5: Paired/unpaired device distinction in UI (Device View) | `test_device_view_inline_assign` | UI | — | ❌ Gap (modal replaced by inline assignment in v1.2 — test needs to be rewritten for new UI) |

---

### Device Data Upload

| Requirement | Test Case | Type | File | Status |
|---|---|---|---|---|
| REQ-UPLOAD-1: POST /devices with batch timestamps | `test_post_device_data_batch_payload` | API | `test_DevicesPost.py` | ✅ Exists |
| REQ-UPLOAD-2: Payload includes device_id, battery, timestamps | `test_post_device_data_success` | API | `test_DevicesPost.py` | ✅ Exists |
| REQ-UPLOAD-3: Explicit trail_id used if provided | `test_explicit_trail_id_respected` | API | — | ❌ Gap |
| REQ-UPLOAD-3: DeviceMetadata cache used if no trail_id | `test_device_trail_association` | API | `test_DeviceTrailAssociation.py` | ✅ Exists (verify) |
| REQ-UPLOAD-3: Defaults to trail_id=0 for unknown device | `test_device_default_trail_id` | API | `test_DeviceDefaultTrailId.py` | ✅ Exists |
| REQ-UPLOAD-4: Duplicate timestamps silently discarded | `test_duplicate_timestamp_rejected` | API | — | ❌ Gap |
| REQ-UPLOAD-5: Timestamps before 2025-01-01 discarded | `test_pre_2025_timestamp_rejected` | API | `test_DevicesPostValidation.py` | ✅ Exists (verify) |
| REQ-UPLOAD-6: Batch of 250 timestamps accepted | `test_post_device_data_batch_payload` | API | `test_DevicesPost.py` | ✅ Exists (verify size) |

---

### Data Storage & Retrieval

| Requirement | Test Case | Type | File | Status |
|---|---|---|---|---|
| REQ-STORE-1: Detection record includes trail_id, timestamp, device_id | `test_get_all_trail_data` | API | `test_GetAllTrailData.py` | ✅ Exists (note: `battery` field is a legacy artifact in TrailDeviceLogs — per-call-in telemetry is now in DeviceCallLog) |
| REQ-STORE-2: Query by trail_id | `test_get_one_trail` | API | `test_GetOneTrail.py` | ✅ Exists |
| REQ-STORE-2: Query filtered by timestamp range | `test_get_trail_data_date_range` | API | — | ❌ Gap (filtering implemented server-side in v1.2 — test still missing) |

---

### Data Visualization — Graph View

| Requirement | Test Case | Type | File | Status |
|---|---|---|---|---|
| REQ-VIZ-1: Chart renders with trail data | `test_one_trail` | UI | `test_OneTrail.py` | ✅ Exists |
| REQ-VIZ-2: Multi-trail selection | `test_multiple_trails` | UI | `test_MultipleTrails.py` | ✅ Exists |
| REQ-VIZ-2: "All Trails" option | `test_all_trails` | UI | `test_AllTrails.py` | ✅ Exists |
| REQ-VIZ-3: Date range selection | `test_edit_dates` | UI | `test_EditDates.py` | ✅ Exists |
| REQ-VIZ-3: Start date picker | `test_edit_start_date` | UI | `test_EditStartDate.py` | ✅ Exists |
| REQ-VIZ-3: End date picker | `test_edit_end_date` | UI | `test_EditEndDate.py` | ✅ Exists |
| REQ-VIZ-4: Granularity options vary by date range | `test_granularity` | UI | `test_granularity.py` | ✅ Exists |
| REQ-VIZ-5: Wilderness area filter | `test_wilderness_groups` | UI | `test_WildernessGroups.py` | ✅ Exists |

---

### Data Visualization — Device View

> **v1.2:** "List View" was renamed to "Device View" and rebuilt as a device-centric table sourced from `DeviceCallLog`. Existing `test_ListView.py` tests reference the old button label ("Switch to List View") and old columns — they need to be updated for the new UI.

| Requirement | Test Case | Type | File | Status |
|---|---|---|---|---|
| REQ-DEV-VIEW-1: Device View renders with device rows | `test_device_view` | UI | `test_ListView.py` | ⚠️ Needs update (old label/columns) |
| REQ-DEV-VIEW-2: Shows device ID, trail, weekly count, firmware, battery, last call-in | `test_device_view_columns` | UI | `test_ListView.py` | ⚠️ Needs update |
| REQ-DEV-VIEW-3: Toggle between graph and device view | `test_view_toggle` | UI | `test_ListView.py` | ⚠️ Needs update (button label changed) |
| REQ-DEV-VIEW-4: Device detail modal shows last 5 call-ins | `test_device_detail_modal` | UI | — | ❌ Gap |

---

### Firmware (Manual / Hardware Required)

| Requirement | Test Case | Type | Method | Status |
|---|---|---|---|---|
| REQ-FW-1: IR sensor detects hiker | Walk past sensor, verify LED flash | Manual | On-device CLI | ✅ Verifiable |
| REQ-FW-2: Timestamps buffered to SD card | Detect hikers offline, verify `fs loginfo` | Manual | CLI `fs loginfo` | ✅ Verifiable |
| REQ-FW-3: Deep sleep between events | Measure current draw in sleep mode | Manual | Hardware | ⚠️ Not routinely tested |
| REQ-FW-4: Battery % reported in upload | Check payload in `modem upload` output | Manual | CLI | ✅ Verifiable |
| REQ-FW-5: Scheduled upload at configured time | Set `upload_time`, wait for RTC wakeup | Manual | CLI + wait | ✅ Verifiable |
| REQ-FW-6: Upload on first power-on | Power cycle device, observe upload | Manual | CLI | ✅ Verifiable |
| REQ-FW-7: Retry on failed upload | Block network, restore, verify upload | Manual | Hardware | ⚠️ Not routinely tested |
| REQ-FW-8: CLI mode accessible | Hold BTN1 on boot, verify `STM32>` prompt | Manual | CLI | ✅ Verifiable |

---

### Non-Functional

| Requirement | Test Case | Type | Tool | Status |
|---|---|---|---|---|
| REQ-NF-2: HTTPS enforced on all endpoints | `test_http_redirect` | API | — | ❌ Gap |
| REQ-NF-4: Buffered data survives connectivity loss | See REQ-FW-7 above | Manual | Hardware | ⚠️ Not routinely tested |
| REQ-NF-5: System handles ~45K records without 502 | `test_scale_45k_records` | Performance | `test_platform/` | ❌ Gap — needs test_platform scenario |

---

## Gap Summary

### High Priority Gaps

| Gap | Requirement | Recommended Action |
|---|---|---|
| Unauthenticated requests return 401 | REQ-AUTH-1 | Add to API test suite |
| Cascading delete unpairs devices | REQ-TRAIL-4 | Extend `test_TrailDelete.py` |
| Duplicate timestamps discarded | REQ-UPLOAD-4 | Add to API test suite |
| Timestamp range filtering returns correct records | REQ-STORE-2 | Add to API test suite (filter now implemented in v1.2) |
| Scale test at large record volume | REQ-NF-5 | New test_platform scenario `near-limit` |
| Lambda timeout regression detection | ISSUES.md #1 | Add response-time assertion to smoke test |

### Medium Priority Gaps

| Gap | Requirement | Recommended Action |
|---|---|---|
| Device reassignment | REQ-DEV-3 | Add to `test_DeviceTrailAssociation.py` |
| Explicit trail_id in device upload respected | REQ-UPLOAD-3 | Add to API test suite |
| Device View UI tests (inline assignment, device detail modal) | REQ-DEV-5, REQ-DEV-VIEW-4 | Rewrite `test_ListView.py` for v1.2 Device View; add device detail modal test |
| HTTPS enforcement | REQ-NF-2 | Add to API test suite |

---

## Performance & Scale Tests (test_platform)

These tests use `test_platform/populate.py` to seed controlled data volumes, then query the API to verify behavior.

### TP-PERF-1: Smoke Load
- **Scenario:** 1 trail, 7 days, ~100 records
- **Purpose:** Baseline — verify API responds at all
- **Pass criteria:** Response in < 3s, HTTP 200, correct record count

### TP-PERF-2: Typical Load
- **Scenario:** All 7 trails, Jan 1 – present (~17K records, current state)
- **Purpose:** Verify normal operating conditions
- **Pass criteria:** Response in < 10s, HTTP 200, no truncation

### TP-PERF-3: Near-Limit Query
- **Scenario:** Single high-traffic trail, full year query (~73K records)
- **Purpose:** Verify system behavior approaching the 10 MB API Gateway per-query response cap (timestamp filtering in v1.2 means this is a per-query limit, not a total-table limit)
- **Pass criteria:** Response in < 30s, HTTP 200, no records dropped; or graceful error if cap exceeded

### TP-PERF-4: Lambda Timeout Regression
- **Scenario:** Same as TP-PERF-2
- **Purpose:** Detect if Lambda timeout has been reverted from 30s to the old 3s default
- **Pass criteria:** Response time < 25s (flags regression before it breaks users)

---

## Smoke Test (Post-Deploy)

Run after every backend deployment. Must complete in < 2 minutes.

1. POST one record to `/devices` with `device_id = test-smoke-<timestamp>` → expect 200
2. GET `/trail_data?trails=<trail_id>` → expect 200, verify record appears
3. GET `/trail_metadata` → expect 200, non-empty list
4. GET `/trail_groups` → expect 200, "All Areas" present
5. DELETE test record (purge by device_id prefix `test-smoke-`)
6. Report pass/fail with response times

**Exit criteria:** All 5 steps pass. Any failure blocks the deployment from going live.

---

## Test Execution

### Running API Tests
```bash
cd swen-project-react-app-API-tests/completed
# Edit config.py: set BASE_URL, COGNITO_TOKEN, API_KEY
pytest -m API -v
```

### Running UI Tests
```bash
cd swen-project-react-app-UI-tests/completed
# Edit config.py: set BASE_URL
# Requires Chrome + ChromeDriver installed
pytest -m UI -v
```

### Running test_platform Performance Tests
```bash
cd test_platform
export TRAIL_API_KEY="..."
python3 populate.py --dry-run   # preview
python3 populate.py             # seed data
# then run API tests against seeded data
```

### Running Smoke Test (post-deploy)
```bash
cd test_platform
export TRAIL_API_KEY="..."
python3 smoke.py   # not yet implemented — see REQUIREMENTS.md R4
```

---

## Entry / Exit Criteria

### Entry (before running tests)
- `config.py` files populated with valid credentials and URLs
- For UI tests: Chrome and ChromeDriver installed and version-matched
- For performance tests: database purged and re-seeded to known state

### Exit (test run complete)
- All ✅ existing tests pass
- No regressions vs previous run
- Gaps noted above are tracked as open issues, not blocking

### Blocking Failures
These failures must be resolved before any code merges to main:
- Any API test returning unexpected 5xx
- Lambda response time > 25s (timeout regression indicator)
- Login/logout UI test failure
- Smoke test failure post-deploy
