#!/usr/bin/env python3
"""
Simulate a new robot-counter device's first call-in.

Finds the highest existing robot-counter-XX number, picks the next one,
and POSTs to /devices with realistic telemetry and a handful of timestamps —
exactly what a real device does on first power-up. The device appears in
Device View unassociated (trail_id=0) with firmware, battery, and signal data
populated, ready to be assigned a trail via the UI.

Usage:
    export TRAIL_API_KEY=<key>
    python3 add_device.py
    python3 add_device.py --dry-run
"""

import argparse
import os
import random
import re
import sys
from datetime import datetime, timezone

import requests

from _auth import auth_headers, base_url


def next_robot_id(session: requests.Session) -> str:
    """Find the highest robot-counter-XX and return the next one."""
    resp = session.get(f"{base_url()}/device_metadata", headers=auth_headers())
    if resp.status_code != 200:
        sys.exit(f"ERROR fetching device_metadata: {resp.status_code} {resp.text}")

    devices = resp.json()
    highest = 0
    for d in devices:
        m = re.match(r"^robot-counter-(\d+)$", d.get("device_id", ""))
        if m:
            highest = max(highest, int(m.group(1)))

    return f"robot-counter-{highest + 1:02d}"


def first_callin_payload(device_id: str) -> dict:
    """Build a realistic first call-in payload — a few hiker detections from today."""
    now = int(datetime.now(timezone.utc).timestamp())
    # A handful of timestamps spread over the past few hours
    count = random.randint(3, 12)
    timestamps = sorted(random.randint(now - 6 * 3600, now - 60) for _ in range(count))
    return {
        "device_id": device_id,
        "firmware_version": "1.1.0",
        "battery": random.randint(88, 99),
        "rssi": random.randint(-110, -75),
        "rsrp": round(random.uniform(-130.0, -85.0), 1),
        "rsrq": round(random.uniform(-18.0, -5.0), 1),
        "data": [{"ts": ts} for ts in timestamps],
    }


def main():
    parser = argparse.ArgumentParser(
        description="Simulate a new robot-counter device's first call-in",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog=__doc__,
    )
    parser.add_argument("--dry-run", action="store_true")
    args = parser.parse_args()

    api_key = os.environ.get("TRAIL_API_KEY", "")
    if not args.dry_run and not api_key:
        sys.exit("Error: set TRAIL_API_KEY environment variable (or use --dry-run)")

    session = requests.Session()
    device_id = next_robot_id(session)
    payload = first_callin_payload(device_id)

    if args.dry_run:
        print(f"[dry-run] Would POST first call-in for {device_id}:")
        print(f"  firmware=1.1.0  battery={payload['battery']}%  "
              f"rssi={payload['rssi']}dBm  {len(payload['data'])} timestamps")
        return

    api_url = os.environ.get("TRAIL_API_URL")
    if not api_url:
        sys.exit(
            "Error: set TRAIL_API_URL environment variable to the target stack's /devices endpoint.\n"
            "Examples:\n"
            "  demo-test: https://api.test.demo.trailcount.io/devices\n"
            "  demo-prod: https://api.demo.trailcount.io/devices\n"
            "  adk-test:  https://api.test.adk.trailcount.io/devices\n"
            "  adk-prod:  https://api.adk.trailcount.io/devices"
        )
    resp = session.post(
        api_url,
        json=payload,
        headers={"X-API-Key": api_key, "Content-Type": "application/json"},
        timeout=30,
    )
    if resp.status_code == 200:
        print(f"Registered {device_id} — unassociated, {len(payload['data'])} detections, "
              f"battery={payload['battery']}%, assign a trail via Device View")
    else:
        sys.exit(f"ERROR: {resp.status_code} {resp.text}")


if __name__ == "__main__":
    main()
