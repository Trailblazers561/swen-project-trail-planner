# Robot Counter — Test Platform Requirements

## Purpose

The robot counter serves three distinct roles:

1. **Historical seed** — populate the database with realistic past data so the frontend has something meaningful to display while real devices are offline or newly deployed.
2. **Nightly simulation** — run each night to add the current day's traffic as if real devices uploaded, keeping the system exercised continuously in real time.
3. **Automated validation** — run after a backend deploy to confirm the system is healthy end-to-end.

---

## Current Capabilities

| Capability | File | Notes |
|---|---|---|
| Bulk historical population | `populate.py` | All trails, configurable date range |
| Single-trail / date-range emulation | `emulator.py` | Mimics firmware payload exactly |
| Database teardown | `purge.py` | Clears all five DynamoDB tables |
| Trail and area setup | `setup_trails.py` | Creates trails and areas from `trails.toml` via API |
| Device association setup | `setup_devices.py` | Assigns device_ids to trails from `trails.toml` via API |
| System state validation | `verify.py` | Checks trails, areas, devices against `trails.toml`; exits 0/1 for CI |
| New device simulation | `add_device.py` | Simulates a real first call-in (POST /devices) for a new robot-counter |
| Domain-realistic traffic | `trails.toml` + `emulator.py` | Seasonality, day-of-week, weather, zero-day probability, fixed seed |
| Dry-run mode | `--dry-run` flag | Preview without hitting the API |

---

## Requirements

### R1 — Nightly Simulation

The robot must be schedulable to run automatically each night, adding one day of simulated traffic (yesterday) for all trails — as if the real devices uploaded that day.

- Runs unattended with no manual intervention
- Adds only the missing day (idempotent — safe to re-run)
- Uses the same seasonality and weather model as bulk population
- Alerts or logs visibly on failure (does not fail silently)
- Scheduling mechanism TBD: cron, AWS EventBridge, or Claude Code scheduled agent

### R2 — Reproducibility

Test runs that use randomness (weather, Gaussian hiker counts) must be reproducible given the same inputs.

- Random seed control: passing `--seed N` produces the identical dataset on every run
- Enables before/after comparisons when testing backend changes
- Bulk population and nightly runs both support seeding

### R3 — Named Test Scenarios

Common test configurations should be expressible as named scenarios rather than requiring the user to assemble flags each time.

Examples:
- `smoke` — one trail, one week, minimal data; verifies the API accepts and returns data
- `peak` — all trails, peak summer weekend; stresses high-volume paths
- `full-season` — all trails, full calendar year; tests the 50K record boundary
- `empty` — purge only; clean slate before a fresh test run

Scenarios defined in `trails.toml` or a separate `scenarios.toml`.

### R4 — Post-Deploy Validation

After a backend deployment, the robot should run a smoke test that:

- POSTs a small number of records to the API
- Queries the API to confirm those records are retrievable
- Checks that the response structure matches what the frontend expects
- Reports pass/fail clearly (exit code 0 / non-zero for CI integration)
- Cleans up the test records it created

### R5 — Performance Measurement

The robot should optionally time API calls and flag regressions.

- Report round-trip time per POST and per GET
- Flag if any call exceeds a configurable threshold (e.g. 10s)
- Useful for catching Lambda timeout regressions before they reach users (see [[ISSUES]] #1)

### R6 — Boundary / Edge Case Coverage

Explicit test scenarios for known system limits:

- Zero-count days (no hikers — verify empty payload handling)
- Maximum batch size (250 timestamps per packet — firmware limit)
- Near-limit record volume — a single high-traffic trail queried over a full year (~200 detections/day × 365 days ≈ 73K records), approaching the API Gateway 10 MB per-query response cap
- Battery drain to minimum (10%)
- Simultaneous multi-trail upload (if ever supported)

### R7 — Observability

The robot's output should make it easy to understand what happened and why.

- Summary line at end: dates covered, records written, bad-weather days, elapsed time
- Verbose mode shows per-day detail; default mode shows per-trail summary only
- Failure messages include the HTTP status, response body, and which trail/day failed
- Nightly runs write a log file with timestamp in the filename

---

## Open Questions

1. **Scheduling mechanism for nightly run** — cron job on a Mac, AWS EventBridge + Lambda, or a Claude Code scheduled agent (`/schedule`)? Needs to run even when the development machine is off.
2. **Test data isolation** — should the robot use separate `device_id` prefixes for smoke/validation runs so test records can be identified and purged without touching nightly simulation data?
3. **Seed persistence** — for the nightly run, should the weather seed be derived from the date (so the same night always produces the same weather) or fully random?
4. **Alert destination** — where should nightly failures be reported? Email, SMS, Slack?
