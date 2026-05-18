#!/usr/bin/env python3
"""
Verify that the live system matches trails.toml.

Checks:
  - Every trail in trails.toml exists (by name) in /trail_metadata
  - Every area in trails.toml exists in /trail_groups
  - Every device_id in trails.toml is associated to the correct trail in /device_metadata

Exits 0 if everything matches, 1 if any check fails (suitable for CI/CD).

Usage:
    export TRAIL_EMAIL=you@example.com
    export TRAIL_PASSWORD=yourpassword
    python3 verify.py
    python3 verify.py --areas "High Peaks"  # check a subset
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


def fetch_json(session: requests.Session, path: str) -> list | dict | None:
    url = f"{base_url()}/{path.lstrip('/')}"
    resp = session.get(url, headers=auth_headers())
    if resp.status_code == 200:
        return resp.json()
    print(f"  ERROR fetching {url}: {resp.status_code} {resp.text}", file=sys.stderr)
    return None


def main():
    config = load_config()
    all_trails = config["trails"]

    parser = argparse.ArgumentParser(
        description="Verify live system matches trails.toml",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog=__doc__,
    )
    parser.add_argument(
        "--areas",
        metavar="AREA",
        nargs="+",
        help="Only check trails in these areas (default: all)",
    )
    args = parser.parse_args()

    selected_trails = all_trails
    if args.areas:
        selected_trails = [t for t in all_trails if t.get("area") in args.areas]
        if not selected_trails:
            sys.exit(f"No trails found for areas: {args.areas}")

    session = requests.Session()
    failures = []

    # --- Check trails ---
    print("Checking trails...")
    trail_meta_raw = fetch_json(session, "trail_metadata")
    if trail_meta_raw is None:
        sys.exit(1)

    live_trails_by_name = {t["trail_name"]: t for t in trail_meta_raw}
    live_trail_id_by_name: dict[str, int] = {}

    for t in selected_trails:
        name = t["name"]
        if name not in live_trails_by_name:
            print(f"  FAIL: trail {name!r} not found in live system")
            failures.append(f"Missing trail: {name!r}")
        else:
            tid = live_trails_by_name[name]["trail_id"]
            live_trail_id_by_name[name] = tid
            print(f"  OK: trail {tid:>3} {name!r}")

    # --- Check areas ---
    areas: dict[str, list] = {}
    for t in selected_trails:
        area = t.get("area", "Uncategorized")
        areas.setdefault(area, []).append(t["name"])

    print("\nChecking areas...")
    groups_raw = fetch_json(session, "trail_groups")
    if groups_raw is None:
        sys.exit(1)

    live_groups = {g["group_name"]: g.get("trail_ids", []) for g in groups_raw}

    for area_name, trail_names in areas.items():
        if area_name not in live_groups:
            print(f"  FAIL: area {area_name!r} not found in live system")
            failures.append(f"Missing area: {area_name!r}")
        else:
            live_ids = set(live_groups[area_name])
            expected_ids = {live_trail_id_by_name[n] for n in trail_names if n in live_trail_id_by_name}
            missing = expected_ids - live_ids
            extra = live_ids - expected_ids
            if missing or extra:
                print(f"  FAIL: area {area_name!r} membership mismatch (missing={missing}, extra={extra})")
                failures.append(f"Area mismatch: {area_name!r}")
            else:
                print(f"  OK: area {area_name!r} ({len(live_ids)} trails)")

    # --- Check device associations ---
    with_device = [t for t in selected_trails if t.get("device_id")]
    if with_device:
        print("\nChecking device associations...")
        devices_raw = fetch_json(session, "device_metadata")
        if devices_raw is None:
            sys.exit(1)

        live_devices = {d["device_id"]: d for d in devices_raw}

        for t in with_device:
            dev = t["device_id"]
            expected_id = live_trail_id_by_name.get(t["name"])
            if dev not in live_devices:
                print(f"  WARN: {dev} not found in device_metadata (may need first call-in)")
            elif expected_id is not None and live_devices[dev].get("current_trail_id") != expected_id:
                live_id = live_devices[dev].get("current_trail_id")
                print(f"  FAIL: {dev} → trail {live_id} (expected {expected_id})")
                failures.append(f"Device mismatch: {dev}")
            else:
                tid = live_devices[dev].get("current_trail_id", "?")
                print(f"  OK: {dev} → trail {tid} ({t['name']!r})")

    print()
    if failures:
        print(f"FAILED — {len(failures)} check(s) failed:")
        for f in failures:
            print(f"  - {f}")
        sys.exit(1)
    else:
        print("All checks passed.")
        sys.exit(0)


if __name__ == "__main__":
    main()
