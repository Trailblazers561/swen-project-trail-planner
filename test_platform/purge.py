#!/usr/bin/env python3
"""
Purge all data from the trail counter DynamoDB tables.

Clears (all names prefixed with --prefix, default "tst-"):
  - {prefix}TrailDeviceLogs  (all hiker timestamp records)
  - {prefix}DeviceCallLog    (all device call-in history)
  - {prefix}DeviceMetadata   (all device/trail associations)
  - {prefix}TrailMetadata    (all trail definitions)
  - {prefix}TrailGroups      (all trail group / area definitions)

Usage:
    python3 purge.py                    # dry run against tst- tables
    python3 purge.py --confirm          # delete from tst- tables
    python3 purge.py --prefix ""        # !! production tables (dangerous) !!
"""

import argparse
import sys
import boto3

TABLES = [
    {"name": "TrailDeviceLogs",  "pk": "trail_id",   "sk": "timestamp"},
    {"name": "DeviceCallLog",    "pk": "device_id",   "sk": "timestamp"},
    {"name": "DeviceMetadata",   "pk": "device_id",   "sk": None},
    {"name": "TrailMetadata",    "pk": "trail_id",    "sk": None},
    {"name": "TrailGroups",      "pk": "group_name",  "sk": None},
]


def purge_table(table_name: str, pk: str, sk: str | None, dry_run: bool) -> int:
    session = boto3.Session(profile_name="trail-admin", region_name="us-east-1")
    dynamodb = session.resource("dynamodb")
    table = dynamodb.Table(table_name)

    items = []
    last_key = None
    print(f"  Scanning {table_name}...", end="", flush=True)
    while True:
        kwargs = {}
        if last_key:
            kwargs["ExclusiveStartKey"] = last_key
        resp = table.scan(**kwargs)
        items.extend(resp.get("Items", []))
        last_key = resp.get("LastEvaluatedKey")
        if not last_key:
            break

    print(f" {len(items)} items", end="")

    if dry_run or not items:
        print()
        return len(items)

    with table.batch_writer() as batch:
        for item in items:
            key = {pk: item[pk]}
            if sk:
                key[sk] = item[sk]
            batch.delete_item(Key=key)

    print(" — deleted")
    return len(items)


def main():
    parser = argparse.ArgumentParser(
        description="Purge all trail counter data from DynamoDB",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog=__doc__,
    )
    parser.add_argument(
        "--prefix",
        default="tst-",
        help='Table name prefix (default: "tst-"). Use "" for production — dangerous!',
    )
    parser.add_argument(
        "--confirm",
        action="store_true",
        help="Actually delete the data (default is dry-run preview)",
    )
    args = parser.parse_args()

    if args.confirm and args.prefix == "":
        print("ERROR: refusing to delete production tables without explicit --prefix \"\".")
        print('Re-run with --prefix "" if you really mean it.')
        sys.exit(1)

    if args.prefix == "" and not args.confirm:
        print("WARNING: --prefix is empty — this targets PRODUCTION tables.")
        print("This is a dry run. Add --confirm to actually delete.\n")

    table_names = [f"{args.prefix}{t['name']}" for t in TABLES]

    if args.confirm:
        print(f"PURGING data from {len(TABLES)} tables (prefix: '{args.prefix}')...\n")
    else:
        print(f"DRY RUN — showing what would be deleted (prefix: '{args.prefix}')\n")

    total = 0
    for t, full_name in zip(TABLES, table_names):
        total += purge_table(full_name, t["pk"], t["sk"], dry_run=not args.confirm)

    print()
    if args.confirm:
        print(f"Done. {total} items deleted across {len(TABLES)} tables.")
    else:
        print(f"Would delete {total} items across {len(TABLES)} tables.")
        print("Run with --confirm to proceed.")


if __name__ == "__main__":
    main()
