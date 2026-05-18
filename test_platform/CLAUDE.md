# Test Platform — Claude Code Context

Python scripts that simulate trail counter device uploads. Three roles: seed historical data into DynamoDB, run nightly to keep the system exercised, and validate the backend after a deploy.

This directory lives inside the webapp repo it tests — see `webapp/CLAUDE.md` for the API/Cognito/DynamoDB it targets, and `webapp/terraform/` for the tenant-stack workspaces (`adk-test`, `adk-prod`, `demo-test`, `demo-prod`) you'd point these scripts at.

**Trail ID 1 (The Garden) note:** The V1 trail counter is targeted for The Garden trailhead (Trail ID 1). Deployment was originally scheduled for ~May 18, 2026 but is **postponed indefinitely as of 2026-05-15**. Once the real device is eventually live, stop running `populate.py` or `emulator.py` for Trail ID 1 to avoid mixing simulated and real data. Use a distinct `device_id` prefix (e.g. `robot-*`) if you need to continue testing against Trail ID 1.

Full requirements and open questions: [[REQUIREMENTS]].

---

## Setup

**Python 3.11+ required** (`tomllib` is stdlib from 3.11).

```bash
pip install boto3 requests
```

**API key** (for `populate.py` and `emulator.py`):
```bash
export TRAIL_API_KEY="<current key>"
```

**AWS credentials** (for `purge.py` only — direct DynamoDB access):
Requires an AWS profile named `trail-admin` in `~/.aws/credentials` with access to the DynamoDB tables.

---

## Rebuild sequence (repeatable)

```bash
# 1. Wipe all data from staging
python3 purge.py --confirm

# 2. Create trails and areas
export TRAIL_EMAIL=... TRAIL_PASSWORD=...
python3 setup_trails.py

# 3. Associate real devices to trails
python3 setup_devices.py --areas "High Peaks" "Five Ponds"

# 4. Associate test devices to test trails
python3 setup_devices.py --areas "Test Area"

# 5. Verify everything matches trails.toml
python3 verify.py

# 6. Populate hiker data (Jan 1 2026 → yesterday)
export TRAIL_API_KEY=...
python3 populate.py
```

---

## Scripts

### populate.py — bulk historical seed

Populates all trails with realistic historical data. Calls `emulator.py` internally for each trail/day.
Reads `device_id`, `zero_day_probability`, and `fixed_seed` from `trails.toml`.

```bash
python3 populate.py                        # all trails, default date range
python3 populate.py --dry-run              # preview without uploading
python3 populate.py --start 2026-03-01     # override start date
python3 populate.py --trails 1 2 3         # specific trail IDs only
python3 populate.py --areas "Test Area"    # specific area only
```

### emulator.py — single-trail emulation

Mimics the firmware exactly: generates timestamped detections and POSTs them in batches of 250, same format as the real device. Supports `zero_day_probability` and `fixed_seed` when called from `populate.py`.

```bash
export TRAIL_API_KEY=<key>
python3 emulator.py --device-id robot-counter-01 --trail-id 1 --days 7
python3 emulator.py --device-id robot-counter-01 --start 2026-04-01 --end 2026-04-30
python3 emulator.py --dry-run --device-id robot-counter-01 --days 3
```

API URL is read from `TRAIL_API_URL` env var or defaults to the production endpoint.
Per-tenant overrides (TrailCount cutover):
- `adk-test`: `export TRAIL_API_URL=https://api.test.adk.trailcount.io/devices`
- `adk-prod`: `export TRAIL_API_URL=https://api.adk.trailcount.io/devices`
- `demo-test`: `export TRAIL_API_URL=https://api.test.demo.trailcount.io/devices`
- `demo-prod`: `export TRAIL_API_URL=https://api.demo.trailcount.io/devices`
- Legacy V1 staging (still up): `export TRAIL_API_URL=https://2u0a6kwthj.execute-api.us-east-1.amazonaws.com/trailplanner_api_stage/devices`

### purge.py — full database teardown

Clears all five DynamoDB tables (with configurable prefix). Requires the `trail-admin` AWS profile.

```bash
python3 purge.py                    # dry run — tst- tables
python3 purge.py --confirm          # delete from tst- tables
python3 purge.py --prefix "" --confirm  # !! production tables !!
```

### setup_trails.py — create trails and areas

Creates trails (POST /trail_metadata) and areas (POST /trail_groups) from trails.toml.
Requires Cognito credentials via `TRAIL_EMAIL` / `TRAIL_PASSWORD` env vars.

```bash
python3 setup_trails.py             # all trails and areas
python3 setup_trails.py --dry-run   # preview
python3 setup_trails.py --areas "Test Area"
```

### setup_devices.py — register device associations

Associates each device_id in trails.toml to its trail via PUT /device_metadata.

```bash
python3 setup_devices.py            # all devices
python3 setup_devices.py --dry-run
python3 setup_devices.py --areas "High Peaks"
```

### verify.py — validate system state

Checks that trails, areas, and device associations in the live system match trails.toml.
Exits 0 on pass, 1 on any failure (suitable for CI).

```bash
python3 verify.py
python3 verify.py --areas "Test Area"
```

### add_device.py — simulate a new robot-counter first call-in

Finds the next robot-counter-XX number and POSTs to `/devices` exactly as a real device does on first power-up: firmware version, battery, signal stats (RSSI/RSRP/RSRQ), and a handful of hiker detections from the past few hours. The device appears in Device View unassociated, with telemetry populated and ready to be assigned a trail via the UI.

Requires `TRAIL_API_KEY`. No Cognito credentials needed.

```bash
python3 add_device.py
python3 add_device.py --dry-run
```

### _auth.py — shared Cognito helper (not invoked directly)

Reads `VITE_API_URL`, `VITE_COGNITO_*` from `../swen-project-react-app/.env` and performs
`USER_PASSWORD_AUTH`. Credentials via `TRAIL_EMAIL` / `TRAIL_PASSWORD` env vars (or interactive prompt).

---

## Traffic model (trails.toml)

`trails.toml` defines per-trail baseline traffic, device assignment, and system-wide seasonality.

```
daily_hikers = summer_weekday_hikers × season_multiplier × dow_multiplier × weather_multiplier
```

| Season | Multiplier |
|--------|-----------|
| Summer (Memorial Day – Columbus Day) | 1.0 |
| Winter (Jan 1 – Mar 14) | 0.3 |
| Spring / Fall | 0.1 |

Weekends are 4× weekdays. ~20% of days get a bad-weather penalty (0.2–0.75×).

Per-trail options: `device_id`, `zero_day_probability` (chance of zero hikers regardless of other multipliers), `fixed_seed` (integer; when set, data for this trail is fully reproducible across runs).

**Current trails (13 across 3 areas):**

| ID | Name | Area | Summer weekday | Device |
|----|------|------|---------------|--------|
| 1 | The Garden | High Peaks | 50 | robot-counter-01 |
| 2 | Heart Lake | High Peaks | 200 | robot-counter-02 |
| 3 | Elk Lake | High Peaks | 20 | robot-counter-03 |
| 4 | Upper Works | High Peaks | 40 | robot-counter-04 |
| 5 | Long Lake NP Trail | High Peaks | 10 | robot-counter-05 |
| 6 | Averyville NP Trail | High Peaks | 5 | robot-counter-06 |
| 7 | Blueberry Trail | High Peaks | 30 | robot-counter-07 |
| 8 | High Rock | Five Ponds | 5 | robot-counter-08 |
| 9 | Janacks Landing | Five Ponds | 5 | robot-counter-09 |
| 10 | Test Trailhead 1 | Test Area | 50 | test-device-001 |
| 11 | Test Trailhead 2 | Test Area | 25 | test-device-002 |
| 12 | Test Trailhead 3 | Test Area | 10 | test-device-003 |
| 13 | Test Trailhead 4 | Test Area | 5 | test-device-004 |

---

## What's not implemented yet

See [[REQUIREMENTS]] for the full requirements list. Items still pending:

- Named test scenarios / `scenarios.toml` (R3)
- Per-call timing and regression detection (R5)
- Nightly scheduling mechanism — unresolved (R1)
