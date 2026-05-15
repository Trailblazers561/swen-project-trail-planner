# Backend Issues & Recommended Changes

Findings from May 7, 2026 debugging session.

---

## Issues Found

### 1. Lambda timeout too short — ✅ FIXED (v1.2)
**Severity: Critical**
`traildata_get_trail_data` had a 3-second timeout. With any real data volume (7 trails × weeks of data), the DynamoDB queries cannot complete in time. API Gateway returns 502, which also strips CORS headers, causing the browser to report a confusing CORS error that masks the real problem.

- **Fixed live (2026-05-07):** timeout increased to 30s via AWS CLI
- **Fixed in code (v1.2):** all 11 Lambda functions set to `timeout = 30` in `terraform/lambdas.tf`

---

### 2. No timestamp filtering in DynamoDB queries — ✅ FIXED (v1.2)
**Severity: High**
`get_trail_data()` in `lambdas/traildata.py` accepted `start` and `end` query parameters but never used them. The DynamoDB `query()` call had no `KeyConditionExpression` for the timestamp sort key — it returned every record ever stored for each trail.

- **Fixed (v1.2):** `start`/`end` are now applied as a `KeyConditionExpression`. Only the requested date range is fetched from DynamoDB.

---

### 3. No DynamoDB pagination — ✅ FIXED (v1.2)
**Severity: High**
All `query()` and `scan()` calls returned only the first page of results (DynamoDB caps each response at 1 MB). If a trail had more than ~10K records, results were silently truncated. The Lambda never checked for `LastEvaluatedKey`.

- **Fixed (v1.2):** `LastEvaluatedKey` loop added to `get_trail_data()` and all metadata endpoints (`get_trail_metadata`, `get_device_metadata`, `get_trail_groups`).

---

### 4. Full table scans on every metadata request
**Severity: Medium**
`get_trail_metadata()`, `get_device_metadata()`, and `get_trail_groups()` all call `scan()` with no filters or `Limit`. These run on every page load and get slower as tables grow. Trail creation also scans TrailMetadata just to find the max ID.

---

### 5. API Gateway 10 MB response size limit
**Severity: Medium** (reduced by Issue #2 fix)
API Gateway hard cap is 10 MB per response. At roughly 150 bytes per JSON record, that is ~65K records per query. With timestamp filtering now in place (Issue #2 fixed), typical dashboard queries (e.g. 1 month, all trails) return well under this limit.

**Remaining edge case:** A single high-traffic trail (200+/day) queried over a full year returns ~73K records (~11 MB) — just over the cap. The dashboard's default date range (Jan 1 of the current year to today) avoids this in practice. No practical total-table size limit exists; the limit is per-query response size only.

---

### 6. Frontend silently swallows API errors — ✅ FIXED (v1.2)
**Severity: Medium**
In `dashboard.tsx`, `getResponse()` wrapped everything in a try/catch that only called `console.error`. When an API call failed (401, 502, network error), the dashboard showed nothing with no user-visible message.

- **Fixed (v1.2):** Dashboard now displays a red error banner when a trail data fetch fails. 401/403 responses redirect to `/login?reason=session_expired`.

---

### 7. CORS errors mask real errors
**Severity: Low (diagnostic)**
API Gateway only includes CORS headers when the Lambda returns a valid response. On Lambda timeout or crash (502), no CORS headers are set. The browser reports a CORS error first, which makes debugging misleading — the actual cause is always a Lambda failure.

---

### 8. Device call-in history modal shows misleading "No call-in history found" on auth failure
**Severity: Medium**
Observed 2026-05-13 on Device View. Clicking a device ID opens `DeviceDetailModal`, which queries `GET /device_call_log?device_id=xxx`. When the Cognito session has expired, the API returns 401/403, but the modal renders "No call-in history found." — the same message it shows for a device that genuinely has no call-in records. The user has no way to tell "session expired, log back in" from "device has never called in."

Issue #6's fix (red error banner + redirect to `/login?reason=session_expired` on 401/403) was applied to `dashboard.tsx` trail data fetches but not to `DeviceDetailModal`'s call-log fetch. Likely also affects other modal-driven fetches.

**Recommended fix:** In `DeviceDetailModal` (and an audit of other modal/component-level `api.ts` consumers), distinguish "fetch succeeded with empty array" from "fetch failed." On 401/403, redirect to `/login?reason=session_expired`. On other errors, show "Could not load call-in history" rather than the empty-state message.

---

## Recommended Changes

Items 1–3 and 6 were completed in v1.2 (branch `v1.2`, deployed to staging, pending production promotion). Items 4, 5, and 8 remain open.

| # | Change | File | Priority | Status |
|---|--------|------|----------|--------|
| 1 | Fix Lambda timeout in Terraform | `terraform/lambdas.tf` — `timeout = 30` for all 11 functions | **High** | ✅ Done (v1.2) |
| 2 | Add timestamp `KeyConditionExpression` to `get_trail_data()` | `lambdas/traildata.py` | **High** | ✅ Done (v1.2) |
| 3 | Add DynamoDB pagination (`LastEvaluatedKey` loop) to all query/scan calls | `lambdas/traildata.py` | **High** | ✅ Done (v1.2) |
| 4 | Replace full-table scans with keyed lookups or add `Limit` | `lambdas/traildata.py` — metadata endpoints | **Medium** | ⬜ Open |
| 5 | Replace sequential trail queries with `batch_get_item` or parallel requests | `lambdas/traildata.py` — `get_trail_data()` loop | **Low** | ⬜ Open |
| 6 | Show user-visible error when trail data fetch fails | `swen-project-react-app/src/dashboard.tsx` | **Medium** | ✅ Done (v1.2) |
| 8 | Distinguish auth-expired from empty-history in `DeviceDetailModal` (and audit other modal fetches) | `swen-project-react-app/src/components/` | **Medium** | ⬜ Open |
