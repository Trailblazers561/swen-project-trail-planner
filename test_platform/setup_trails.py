#!/usr/bin/env python3
"""
Create trails and areas from trails.toml via the API.

Reads trails.toml, creates each trail via POST /trail_metadata, then creates
each area (group) via POST /trail_groups containing the right trail IDs.

This is step 2 of the rebuild sequence (after purge.py --confirm).

Usage:
    export TRAIL_EMAIL=you@example.com
    export TRAIL_PASSWORD=yourpassword
    python3 setup_trails.py           # create all trails and areas
    python3 setup_trails.py --dry-run # preview only
    python3 setup_trails.py --areas "High Peaks" "Five Ponds"  # specific areas only
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


def create_trail(session: requests.Session, name: str, area: str | None, dry_run: bool) -> int | None:
    """POST /trail_metadata with optional trail_group. Returns assigned trail_id or None on error."""
    if dry_run:
        area_str = f" in {area!r}" if area else ""
        print(f"  [dry-run] Would create trail: {name!r}{area_str}")
        return None

    url = f"{base_url()}/trail_metadata"
    body: dict = {"trail_name": name}
    if area:
        body["trail_group"] = area
    resp = session.post(url, json=body, headers=auth_headers())
    if resp.status_code in (200, 201):
        data = resp.json()
        tid = data.get("trail_id")
        area_str = f" [{area}]" if area else ""
        print(f"  Created trail {tid:>3}: {name!r}{area_str}")
        return tid
    else:
        print(f"  ERROR creating {name!r}: {resp.status_code} {resp.text}", file=sys.stderr)
        return None


def main():
    config = load_config()
    trails = config["trails"]

    parser = argparse.ArgumentParser(
        description="Create trails and areas from trails.toml",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog=__doc__,
    )
    parser.add_argument("--dry-run", action="store_true")
    parser.add_argument(
        "--areas",
        metavar="AREA",
        nargs="+",
        help="Only create trails and areas matching these area names (default: all)",
    )
    args = parser.parse_args()

    # Filter trails by area if requested
    selected_trails = trails
    if args.areas:
        selected_trails = [t for t in trails if t.get("area") in args.areas]
        if not selected_trails:
            sys.exit(f"No trails found for areas: {args.areas}")

    session = requests.Session()
    name_to_id: dict[str, int] = {}

    print(f"\nCreating {len(selected_trails)} trail(s)...")
    for t in selected_trails:
        area = t.get("area")
        tid = create_trail(session, t["name"], area, args.dry_run)
        if tid is not None:
            name_to_id[t["name"]] = tid

    print("\nDone.")
    if not args.dry_run and name_to_id:
        print("NOTE: Trail IDs assigned by the server may differ from trails.toml IDs.")
        print("Run verify.py to check, then update trails.toml if needed.")


if __name__ == "__main__":
    main()
