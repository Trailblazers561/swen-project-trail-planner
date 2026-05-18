#!/usr/bin/env python3
"""
Register device-to-trail associations from trails.toml via the API.

Reads trails.toml, maps each device_id to its trail_id via PUT /device_metadata.
This pre-registers all devices so uploads are attributed to the correct trail
even before the first real device call-in.

This is step 3 (real devices) and step 4 (test devices) of the rebuild sequence.

Usage:
    export TRAIL_EMAIL=you@example.com
    export TRAIL_PASSWORD=yourpassword
    python3 setup_devices.py                    # all devices
    python3 setup_devices.py --dry-run          # preview only
    python3 setup_devices.py --areas "Test Area"  # only test devices
"""

import argparse
import sys
import tomllib
from pathlib import Path

import requests

from _auth import auth_headers, base_url

CONFIG_FILE = Path(__file__).parent / "trails.toml"


def load_config() -> dict:
    with open(CONFIG_FILE, "rb") as f:
        return tomllib.load(f)


def associate(session: requests.Session, device_id: str, trail_id: int, trail_name: str, dry_run: bool) -> bool:
    if dry_run:
        print(f"  [dry-run] Would associate {device_id} → trail {trail_id} ({trail_name!r})")
        return True

    url = f"{base_url()}/device_metadata"
    resp = session.put(
        url,
        json={"device_id": device_id, "trail_id": trail_id},
        headers=auth_headers(),
    )
    if resp.status_code in (200, 201):
        print(f"  {device_id} → trail {trail_id} ({trail_name!r})")
        return True
    else:
        print(f"  ERROR: {device_id}: {resp.status_code} {resp.text}", file=sys.stderr)
        return False


def main():
    config = load_config()
    trails = config["trails"]

    parser = argparse.ArgumentParser(
        description="Register device-to-trail associations from trails.toml",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog=__doc__,
    )
    parser.add_argument("--dry-run", action="store_true")
    parser.add_argument(
        "--areas",
        metavar="AREA",
        nargs="+",
        help="Only register devices for trails in these areas (default: all)",
    )
    args = parser.parse_args()

    selected = trails
    if args.areas:
        selected = [t for t in trails if t.get("area") in args.areas]
        if not selected:
            sys.exit(f"No trails found for areas: {args.areas}")

    # Filter to trails that have a device_id
    with_device = [t for t in selected if t.get("device_id")]
    without_device = [t for t in selected if not t.get("device_id")]

    if without_device:
        print(f"WARNING: {len(without_device)} trail(s) have no device_id — skipping:")
        for t in without_device:
            print(f"  Trail {t['id']}: {t['name']!r}")
        print()

    session = requests.Session()

    # Look up live trail IDs by name (server-assigned IDs may differ from trails.toml)
    resp = session.get(f"{base_url()}/trail_metadata", headers=auth_headers())
    if resp.status_code != 200:
        sys.exit(f"ERROR fetching trail_metadata: {resp.status_code} {resp.text}")
    live_id_by_name = {t["trail_name"]: t["trail_id"] for t in resp.json()}

    print(f"Associating {len(with_device)} device(s)...\n")
    errors = 0
    for t in with_device:
        trail_id = live_id_by_name.get(t["name"])
        if trail_id is None:
            print(f"  SKIP: trail {t['name']!r} not found in live system — run setup_trails.py first", file=sys.stderr)
            errors += 1
            continue
        ok = associate(session, t["device_id"], trail_id, t["name"], args.dry_run)
        if not ok:
            errors += 1

    print(f"\nDone. {len(with_device) - errors} succeeded, {errors} failed.")


if __name__ == "__main__":
    main()
