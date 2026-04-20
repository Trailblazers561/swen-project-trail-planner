import argparse
import boto3
import csv
from datetime import datetime, timedelta
from zoneinfo import ZoneInfo
from pathlib import Path
from decimal import Decimal

dynamodb = boto3.resource('dynamodb')

def load_test_data(env):
    # Load Tables
    hour_table = dynamodb.Table(f"{env}_DeviceTrailLogHour")
    day_table = dynamodb.Table(f"{env}_DeviceTrailLogDay")
    week_table = dynamodb.Table(f"{env}_DeviceTrailLogWeek")
    month_table = dynamodb.Table(f"{env}_DeviceTrailLogMonth")
    trail_table = dynamodb.Table(f"{env}_Trail")
    device_table = dynamodb.Table(f"{env}_Device")
    device_trail_table = dynamodb.Table(f"{env}_DeviceTrail")
    trail_group_table = dynamodb.Table(f"{env}_TrailGroup")

    # Delete Table Items
    for table in [hour_table, day_table, week_table, month_table]:
        response = table.scan()
        data = response.get('Items')
        
        while 'LastEvaluatedKey' in response:
            response = table.scan(ExclusiveStartKey=response['LastEvaluatedKey'])
            data.extend(response['Items'])

        with table.batch_writer() as batch:
            for item in data:
                batch.delete_item(Key={
                    "device_trail_id": item["device_trail_id"],
                    "start": item["start"]
                })

    # Load Hour Data
    with open(Path(__file__).parent / "hours.csv") as f:
        reader = csv.DictReader(f)
        with hour_table.batch_writer() as batch:
            for row in reader:
                batch.put_item(
                    Item={
                        "device_trail_id": int(row["device_trail_id"]),
                        "start": int(row["start"]),
                        "count": int(row["count"])
                    }
                )

    # Load Day Data
    with open(Path(__file__).parent / "days.csv") as f:
        reader = csv.DictReader(f)
        with day_table.batch_writer() as batch:
            for row in reader:
                batch.put_item(
                    Item={
                        "device_trail_id": int(row["device_trail_id"]),
                        "start": int(row["start"]),
                        "count": int(row["count"]),
                        "battery": int(row["battery"]),
                    }
                )

    # Load Week Data
    with open(Path(__file__).parent / "weeks.csv") as f:
        reader = csv.DictReader(f)
        with week_table.batch_writer() as batch:
            for row in reader:
                batch.put_item(
                    Item={
                        "device_trail_id": int(row["device_trail_id"]),
                        "start": int(row["start"]),
                        "count": int(row["count"]),
                        "battery": int(row["battery"]),
                    }
                )

    # Load Month Data
    with open(Path(__file__).parent / "months.csv") as f:
        reader = csv.DictReader(f)
        with month_table.batch_writer() as batch:
            for row in reader:
                batch.put_item(
                    Item={
                        "device_trail_id": int(row["device_trail_id"]),
                        "start": int(row["start"]),
                        "count": int(row["count"]),
                        "battery": int(row["battery"]),
                    }
                )

    # Load Recent Day Data
    with open(Path(__file__).parent / "days_recent.csv") as f:
        reader = csv.DictReader(f)
        with day_table.batch_writer() as batch:
            current_midnight = datetime.now().astimezone(ZoneInfo("America/New_York")).replace(hour=0, minute=0, second=0, microsecond=0)
            for row in reader:
                batch.put_item(
                    Item={
                        "device_trail_id": int(row["device_trail_id"]),
                        "start": int((current_midnight - timedelta(days=int(row["days_ago"]))).timestamp()),
                        "count": int(row["count"]),
                        "battery": int(row["battery"]),
                    }
                )

    # Load Test Trail Data
    with open(Path(__file__).parent / "test_trails.csv") as f:
        reader = csv.DictReader(f)
        with trail_table.batch_writer() as batch:
            for row in reader:
                batch.put_item(
                    Item={
                        "id": int(row["id"]),
                        "name": row["name"],
                        "latitude": Decimal(row["latitude"]),
                        "longitude": Decimal(row["longitude"]),
                        "notes": row["notes"],
                        "date_activated": int(row["date_activated"])
                    }
                )

    # Load Test Device Data
    with open(Path(__file__).parent / "test_devices.csv") as f:
        reader = csv.DictReader(f)
        with device_table.batch_writer() as batch:
            for row in reader:
                batch.put_item(
                    Item={
                        "id": int(row["id"]),
                        "name": row["name"],
                        "notes": row["notes"],
                        "firmware_version": row["firmware_version"],
                        "date_manufactured": int(row["date_manufactured"])
                    }
                )

    # Load Test Device Trail Data
    with open(Path(__file__).parent / "test_device_trails.csv") as f:
        reader = csv.DictReader(f)
        with device_trail_table.batch_writer() as batch:
            for row in reader:
                batch.put_item(
                    Item={
                        "id": int(row["id"]),
                        "device_id": int(row["device_id"]),
                        "trail_id": int(row["trail_id"]),
                        "notes": row["notes"],
                        "date_installed": int(row["date_installed"])
                    }
                )

    # Load Test Trail Group Data
    with open(Path(__file__).parent / "test_trail_groups.csv") as f:
        reader = csv.DictReader(f)
        groups = {}
        for row in reader:
            if not groups.get(row["name"]):
                groups[row["name"]] = []
            groups[row["name"]].append(int(row["trail_id"]))
        with trail_group_table.batch_writer() as batch:
            for name, trail_ids in groups.items():
                batch.put_item(
                    Item={
                        "name": name,
                        "trail_ids": trail_ids,
                    }
                )

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--env", required=True)
    args = parser.parse_args()
    load_test_data(args.env)