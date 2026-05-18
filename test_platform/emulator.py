#!/usr/bin/env python3
"""
Trail counter device emulator.

Mimics the real STM32/XBee device: generates hiker detection timestamps and
POSTs them to the AWS API in the same format the firmware uses.

Usage:
    export TRAIL_API_KEY=<your-api-key>
    python emulator.py --device-id robot-counter-001 --trail-id 1 --days 7
    python emulator.py --device-id robot-counter-001 --start 2026-04-01 --end 2026-04-30
    python emulator.py --dry-run --device-id robot-counter-001 --days 3
"""

import argparse
import os
import random
import sys
import time
from datetime import date, datetime, timedelta, timezone

import requests

API_URL = os.environ.get("TRAIL_API_URL")

# Matches firmware: NUM_TIMESTAMPS_PER_PACKET
BATCH_SIZE = 250

# Realistic hiker traffic weights by hour (0–23).
# Bimodal: morning peak ~9am, afternoon peak ~2pm. Near-zero overnight.
HOUR_WEIGHTS = [
    0.0,  # 00
    0.0,  # 01
    0.0,  # 02
    0.0,  # 03
    0.0,  # 04
    0.2,  # 05 — very early
    1.0,  # 06
    2.5,  # 07
    5.0,  # 08
    7.0,  # 09 — morning peak
    6.5,  # 10
    5.5,  # 11
    5.0,  # 12
    4.5,  # 13
    6.0,  # 14 — afternoon peak
    7.0,  # 15
    6.5,  # 16
    5.0,  # 17
    3.0,  # 18
    1.5,  # 19
    0.5,  # 20
    0.1,  # 21
    0.0,  # 22
    0.0,  # 23
]

_HOUR_TOTAL = sum(HOUR_WEIGHTS)
_HOUR_CDF = []
_running = 0.0
for w in HOUR_WEIGHTS:
    _running += w / _HOUR_TOTAL
    _HOUR_CDF.append(_running)


def pick_hour() -> int:
    r = random.random()
    for h, cdf in enumerate(_HOUR_CDF):
        if r <= cdf:
            return h
    return 23


def generate_timestamps(day: date, count: int) -> list[int]:
    """Return `count` Unix timestamps spread realistically across `day`."""
    ts_list = []
    for _ in range(count):
        hour = pick_hour()
        minute = random.randint(0, 59)
        second = random.randint(0, 59)
        dt = datetime(day.year, day.month, day.day, hour, minute, second, tzinfo=timezone.utc)
        ts_list.append(int(dt.timestamp()))
    ts_list.sort()
    return ts_list


def build_payload(device_id: str, battery: int, timestamps: list[int]) -> dict:
    """Match firmware create_json_body() format exactly."""
    return {
        "device_id": device_id,
        "firmware_version": "1.1.0",
        "rssi": random.randint(-115, -85),
        "rsrp": round(random.uniform(-140.0, -90.0), 1),
        "rsrq": round(random.uniform(-20.0, -5.0), 1),
        "battery": battery,
        "data": [{"ts": ts} for ts in timestamps],
    }


def send_batch(
    session: requests.Session,
    api_key: str,
    device_id: str,
    battery: int,
    timestamps: list[int],
    dry_run: bool,
    trail_id: int | None,
) -> bool:
    payload = build_payload(device_id, battery, timestamps)
    if trail_id is not None:
        payload["trail_id"] = trail_id

    if dry_run:
        first_ts = datetime.fromtimestamp(timestamps[0], tz=timezone.utc).strftime("%Y-%m-%d %H:%M")
        last_ts = datetime.fromtimestamp(timestamps[-1], tz=timezone.utc).strftime("%Y-%m-%d %H:%M")
        print(f"  [dry-run] Would POST {len(timestamps)} timestamps ({first_ts} → {last_ts})")
        return True

    resp = session.post(
        API_URL,
        json=payload,
        headers={"X-API-Key": api_key, "Content-Type": "application/json"},
        timeout=30,
    )

    if resp.status_code == 200:
        return True

    print(f"  ERROR {resp.status_code}: {resp.text}", file=sys.stderr)
    return False


def run(args: argparse.Namespace) -> None:
    api_key = os.environ.get("TRAIL_API_KEY", "")
    if not args.dry_run and not api_key:
        sys.exit("Error: set TRAIL_API_KEY environment variable (or use --dry-run to test without it)")
    if not args.dry_run and not API_URL:
        sys.exit(
            "Error: set TRAIL_API_URL environment variable to the target stack's /devices endpoint.\n"
            "Examples:\n"
            "  demo-test:  https://api.test.demo.trailcount.io/devices\n"
            "  demo-prod:  https://api.demo.trailcount.io/devices\n"
            "  adk-test:   https://api.test.adk.trailcount.io/devices\n"
            "  adk-prod:   https://api.adk.trailcount.io/devices\n"
            "  legacy tst: https://2u0a6kwthj.execute-api.us-east-1.amazonaws.com/trailplanner_api_stage/devices"
        )

    # Build date range
    if args.start and args.end:
        start_date = date.fromisoformat(args.start)
        end_date = date.fromisoformat(args.end)
    elif args.days:
        end_date = date.today() - timedelta(days=1)  # yesterday, so all data is in the past
        start_date = end_date - timedelta(days=args.days - 1)
    else:
        sys.exit("Error: specify either --days or both --start and --end")

    if start_date > end_date:
        sys.exit("Error: --start must be before --end")

    day_count = (end_date - start_date).days + 1
    day_multiplier_fn = getattr(args, "day_multiplier_fn", None)
    weather_by_date = getattr(args, "weather_by_date", {})
    weekend_multiplier = getattr(args, "weekend_multiplier", 1.0)
    zero_day_probability = getattr(args, "zero_day_probability", 0.0)
    fixed_seed = getattr(args, "fixed_seed", None)

    print(f"Device:    {args.device_id}")
    print(f"Trail ID:  {args.trail_id if args.trail_id is not None else '(server auto-resolves)'}")
    print(f"Date range: {start_date} → {end_date} ({day_count} days)")
    if day_multiplier_fn:
        print(f"Hikers/day: ~{args.hikers_per_day} (summer weekday baseline; varies by season + day)")
    else:
        print(f"Hikers/day: ~{args.hikers_per_day} weekday / ~{int(args.hikers_per_day * weekend_multiplier)} weekend")
    if fixed_seed is not None:
        print(f"Seed:      {fixed_seed} (reproducible)")
    if zero_day_probability:
        print(f"Zero-day:  {zero_day_probability:.0%} chance")
    print(f"Mode:      {'DRY RUN' if args.dry_run else 'LIVE'}")
    print()

    session = requests.Session()
    total_sent = 0
    total_errors = 0
    battery = 95  # start with full battery, drain slowly

    current = start_date
    day_index = 0
    while current <= end_date:
        # Per-day seed: fixed_seed trails are fully reproducible across runs;
        # non-fixed trails get a new random sequence each run (no seed set).
        if fixed_seed is not None:
            random.seed(fixed_seed + day_index)

        # Zero-day check: some low-traffic trails have occasional zero-hiker days
        if zero_day_probability and random.random() < zero_day_probability:
            print(f"{current}    0 hikers (zero day)  ✓")
            current += timedelta(days=1)
            day_index += 1
            continue

        base = args.hikers_per_day
        if day_multiplier_fn:
            base = base * day_multiplier_fn(current)
        elif current.weekday() >= 5:
            base = int(base * weekend_multiplier)
        base = base * weather_by_date.get(current, 1.0)
        daily_count = max(0, int(random.gauss(base, base * 0.3)))

        timestamps = generate_timestamps(current, daily_count)

        # Battery drains slowly over time
        battery = max(10, battery - random.randint(0, 1))

        print(f"{current}  {daily_count:3d} hikers", end="")

        # Send in batches matching real firmware packet size
        batches = [timestamps[i:i + BATCH_SIZE] for i in range(0, max(len(timestamps), 1), BATCH_SIZE)]
        if not timestamps:
            batches = [[]]  # send one empty-ish packet like the real device would

        ok = True
        for batch in batches:
            if not batch:
                # Nothing to send today — skip entirely (emulator doesn't need the empty-packet behavior)
                continue
            success = send_batch(session, api_key, args.device_id, battery, batch, args.dry_run, args.trail_id)
            if success:
                total_sent += len(batch)
            else:
                total_errors += 1
                ok = False
            if not args.dry_run:
                time.sleep(0.2)  # be polite to the API

        if ok:
            print("  ✓")
        else:
            print("  ✗ (some batches failed)")

        current += timedelta(days=1)
        day_index += 1

    print()
    print(f"Done. {total_sent} timestamps uploaded across {day_count} days.", end="")
    if total_errors:
        print(f" {total_errors} batch error(s).")
    else:
        print()



def main() -> None:
    parser = argparse.ArgumentParser(
        description="Trail counter device emulator — generates and uploads fake hiker data",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog=__doc__,
    )
    parser.add_argument(
        "--device-id",
        default="robot-counter-001",
        help="Device ID string sent in the payload (default: robot-counter-001)",
    )
    parser.add_argument(
        "--trail-id",
        type=int,
        default=None,
        help="Trail ID to tag data with. Omit to let server auto-resolve.",
    )
    parser.add_argument(
        "--hikers-per-day",
        type=int,
        default=40,
        metavar="N",
        help="Average hiker detections per day (default: 40)",
    )
    parser.add_argument(
        "--days",
        type=int,
        metavar="N",
        help="Number of past days to generate data for (e.g. --days 7 = last 7 days)",
    )
    parser.add_argument("--start", metavar="YYYY-MM-DD", help="Start date (inclusive)")
    parser.add_argument("--end", metavar="YYYY-MM-DD", help="End date (inclusive)")
    parser.add_argument(
        "--weekend-multiplier",
        type=float,
        default=1.0,
        metavar="X",
        help="Traffic multiplier for Sat/Sun vs weekdays (default: 1.0 = no difference)",
    )
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Print what would be sent without actually calling the API",
    )

    args = parser.parse_args()

    if not args.days and not (args.start and args.end):
        parser.error("specify either --days N or both --start YYYY-MM-DD --end YYYY-MM-DD")
    if bool(args.start) != bool(args.end):
        parser.error("--start and --end must be used together")

    run(args)


if __name__ == "__main__":
    main()
