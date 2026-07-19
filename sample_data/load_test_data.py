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
    device_table = dynamodb.Table(f"{env}_trailcount_device_table")
    trail_table = dynamodb.Table(f"{env}_trailcount_trail_table")
    device_trail_table = dynamodb.Table(f"{env}_trailcount_device_trail_table")
    area_table = dynamodb.Table(f"{env}_trailcount_area_table")
    hour_log_table = dynamodb.Table(f"{env}_trailcount_device_trail_log_hour_table")
    day_log_table = dynamodb.Table(f"{env}_trailcount_device_trail_log_day_table")
    week_log_table = dynamodb.Table(f"{env}_trailcount_device_trail_log_week_table")
    month_log_table = dynamodb.Table(f"{env}_trailcount_device_trail_log_month_table")
    device_log_table = dynamodb.Table(f"{env}_trailcount_device_log_table")
    registration_table = dynamodb.Table(f"{env}_trailcount_registration_table")

    reset_device_table(device_table)
    reset_trail_table(trail_table)
    reset_device_trail_table(device_trail_table)
    reset_area_table(area_table)
    reset_hour_log_table(hour_log_table)
    reset_day_log_table(day_log_table)
    reset_week_log_table(week_log_table)
    reset_month_log_table(month_log_table)
    reset_device_log_table(device_log_table)
    reset_registration_table(registration_table)

def reset_device_table(device_table):
    # Delete Device Data
    response = device_table.scan()
    data = response.get('Items')

    while 'LastEvaluatedKey' in response:
        response = device_table.scan(ExclusiveStartKey=response['LastEvaluatedKey'])
        data.extend(response['Items'])

    with device_table.batch_writer() as batch:
        for item in data:
            batch.delete_item(Key={
                "id": item["id"]
            })

    # Load Device Data
    with open(Path(__file__).parent / "devices.csv") as f:
        reader = csv.DictReader(f)
        with device_table.batch_writer() as batch:
            for row in reader:
                batch.put_item(
                    Item={
                        "id": int(row["id"]),
                        "name": row["name"],
                        "notes": row["notes"],
                        "date_manufactured": int(row["date_manufactured"])
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
                        "date_manufactured": int(row["date_manufactured"])
                    }
                )

def reset_trail_table(trail_table):
    # Delete Trail Data
    response = trail_table.scan()
    data = response.get('Items')

    while 'LastEvaluatedKey' in response:
        response = trail_table.scan(ExclusiveStartKey=response['LastEvaluatedKey'])
        data.extend(response['Items'])

    with trail_table.batch_writer() as batch:
        for item in data:
            batch.delete_item(Key={
                "id": item["id"]
            })

    # Load Trail Data
    with open(Path(__file__).parent / "trails.csv") as f:
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

def reset_device_trail_table(device_trail_table):
    # Delete Device Trail Data
    response = device_trail_table.scan()
    data = response.get('Items')

    while 'LastEvaluatedKey' in response:
        response = device_trail_table.scan(ExclusiveStartKey=response['LastEvaluatedKey'])
        data.extend(response['Items'])

    with device_trail_table.batch_writer() as batch:
        for item in data:
            batch.delete_item(Key={
                "device_id": item["device_id"],
                "date_installed": item["date_installed"]
            })

    # Load Device Trail Data
    with open(Path(__file__).parent / "device_trails.csv") as f:
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

def reset_area_table(area_table):
    # Delete Area Data
    response = area_table.scan()
    data = response.get('Items')

    while 'LastEvaluatedKey' in response:
        response = area_table.scan(ExclusiveStartKey=response['LastEvaluatedKey'])
        data.extend(response['Items'])

    with area_table.batch_writer() as batch:
        for item in data:
            batch.delete_item(Key={
                "name": item["name"]
            })

    # Load Area Data
    with open(Path(__file__).parent / "areas.csv") as f:
        reader = csv.DictReader(f)
        areas = {}
        for row in reader:
            if not areas.get(row["name"]):
                areas[row["name"]] = []
            areas[row["name"]].append(int(row["trail_id"]))
        with area_table.batch_writer() as batch:
            for name, trail_ids in areas.items():
                batch.put_item(
                    Item={
                        "name": name,
                        "trail_ids": trail_ids,
                    }
                )

    # Load Test Area Data
    with open(Path(__file__).parent / "test_areas.csv") as f:
        reader = csv.DictReader(f)
        areas = {}
        for row in reader:
            if not areas.get(row["name"]):
                areas[row["name"]] = []
            areas[row["name"]].append(int(row["trail_id"]))
        with area_table.batch_writer() as batch:
            for name, trail_ids in areas.items():
                batch.put_item(
                    Item={
                        "name": name,
                        "trail_ids": trail_ids,
                    }
                )

def reset_hour_log_table(hour_log_table):
    # Delete Hour Data
    response = hour_log_table.scan()
    data = response.get('Items')

    while 'LastEvaluatedKey' in response:
        response = hour_log_table.scan(ExclusiveStartKey=response['LastEvaluatedKey'])
        data.extend(response['Items'])

    with hour_log_table.batch_writer() as batch:
        for item in data:
            batch.delete_item(Key={
                "device_trail_id": item["device_trail_id"],
                "start": item["start"]
            })

    # Load Hour Data
    with open(Path(__file__).parent / "hour_logs.csv") as f:
        reader = csv.DictReader(f)
        with hour_log_table.batch_writer() as batch:
            for row in reader:
                batch.put_item(
                    Item={
                        "device_trail_id": int(row["device_trail_id"]),
                        "start": int(row["start"]),
                        "count": int(row["count"])
                    }
                )

def reset_day_log_table(day_log_table):
    # Delete Day Data
    response = day_log_table.scan()
    data = response.get('Items')

    while 'LastEvaluatedKey' in response:
        response = day_log_table.scan(ExclusiveStartKey=response['LastEvaluatedKey'])
        data.extend(response['Items'])

    with day_log_table.batch_writer() as batch:
        for item in data:
            batch.delete_item(Key={
                "device_trail_id": item["device_trail_id"],
                "start": item["start"]
            })

    # Load Day Data
    with open(Path(__file__).parent / "day_logs.csv") as f:
        reader = csv.DictReader(f)
        with day_log_table.batch_writer() as batch:
            for row in reader:
                batch.put_item(
                    Item={
                        "device_trail_id": int(row["device_trail_id"]),
                        "start": int(row["start"]),
                        "count": int(row["count"])
                    }
                )

    # Load Recent Day Data
    with open(Path(__file__).parent / "days_recent.csv") as f:
        reader = csv.DictReader(f)
        with day_log_table.batch_writer() as batch:
            current_midnight = datetime.now().astimezone(ZoneInfo("America/New_York")).replace(hour=0, minute=0, second=0, microsecond=0)
            for row in reader:
                batch.put_item(
                    Item={
                        "device_trail_id": int(row["device_trail_id"]),
                        "start": int((current_midnight - timedelta(days=int(row["days_ago"]))).timestamp()),
                        "count": int(row["count"]),
                    }
                )

def reset_week_log_table(week_log_table):
    # Delete Week Data
    response = week_log_table.scan()
    data = response.get('Items')

    while 'LastEvaluatedKey' in response:
        response = week_log_table.scan(ExclusiveStartKey=response['LastEvaluatedKey'])
        data.extend(response['Items'])

    with week_log_table.batch_writer() as batch:
        for item in data:
            batch.delete_item(Key={
                "device_trail_id": item["device_trail_id"],
                "start": item["start"]
            })

    # Load Week Data
    with open(Path(__file__).parent / "week_logs.csv") as f:
        reader = csv.DictReader(f)
        with week_log_table.batch_writer() as batch:
            for row in reader:
                batch.put_item(
                    Item={
                        "device_trail_id": int(row["device_trail_id"]),
                        "start": int(row["start"]),
                        "count": int(row["count"])
                    }
                )

def reset_month_log_table(month_log_table):
    # Delete Month Data
    response = month_log_table.scan()
    data = response.get('Items')

    while 'LastEvaluatedKey' in response:
        response = month_log_table.scan(ExclusiveStartKey=response['LastEvaluatedKey'])
        data.extend(response['Items'])

    with month_log_table.batch_writer() as batch:
        for item in data:
            batch.delete_item(Key={
                "device_trail_id": item["device_trail_id"],
                "start": item["start"]
            })

    # Load Month Data
    with open(Path(__file__).parent / "month_logs.csv") as f:
        reader = csv.DictReader(f)
        with month_log_table.batch_writer() as batch:
            for row in reader:
                batch.put_item(
                    Item={
                        "device_trail_id": int(row["device_trail_id"]),
                        "start": int(row["start"]),
                        "count": int(row["count"])
                    }
                )

def reset_device_log_table(device_log_table):
    # Delete Device Log Data
    response = device_log_table.scan()
    data = response.get('Items')

    while 'LastEvaluatedKey' in response:
        response = device_log_table.scan(ExclusiveStartKey=response['LastEvaluatedKey'])
        data.extend(response['Items'])

    with device_log_table.batch_writer() as batch:
        for item in data:
            batch.delete_item(Key={
                "device_id": item["device_id"],
                "time": item["time"]
            })

    # Load Log Data
    with open(Path(__file__).parent / "device_logs.csv") as f:
        reader = csv.DictReader(f)
        with device_log_table.batch_writer() as batch:
            for row in reader:
                batch.put_item(
                    Item={
                        "device_id": int(row["device_id"]),
                        "time": int(row["time"]),
                        "count": int(row["count"]),
                        "battery": int(row["battery"]),
                        "firmware_version": row["device_id"],
                        "rssi": int(row["rssi"]),
                        "rsrp": int(row["rsrp"]),
                        "rsrq": int(row["rsrq"]),
                    }
                )

    # Load Recent Log Data
    with open(Path(__file__).parent / "logs_recent.csv") as f:
        reader = csv.DictReader(f)
        with device_log_table.batch_writer() as batch:
            current_midnight = datetime.now().astimezone(ZoneInfo("America/New_York")).replace(hour=0, minute=0, second=0, microsecond=0)
            for row in reader:
                batch.put_item(
                    Item={
                        "device_id": int(row["device_id"]),
                        "time": int((current_midnight - timedelta(days=int(row["days_ago"]))).timestamp()),
                        "count": int(row["count"]),
                        "battery": int(row["battery"]),
                        "firmware_version": row["device_id"],
                        "rssi": int(row["rssi"]),
                        "rsrp": int(row["rsrp"]),
                        "rsrq": int(row["rsrq"]),
                    }
                )

def reset_registration_table(registration_table):
    # Delete Registration Data
    response = registration_table.scan()
    data = response.get("Items", [])

    while "LastEvaluatedKey" in response:
        response = registration_table.scan(
            ExclusiveStartKey=response["LastEvaluatedKey"]
        )
        data.extend(response["Items"])

    with registration_table.batch_writer() as batch:
        for item in data:
            batch.delete_item(
                Key={
                    "registration_id": item["registration_id"]
                }
            )

    # Load Registrations Data
    with open(Path(__file__).parent / "registrations.csv") as f:
        reader = csv.DictReader(f)

        with registration_table.batch_writer() as batch:
            for row in reader:
                batch.put_item(
                    Item={
                        "registration_id": int(row["registration_id"]),
                        "device_id": int(row["device_id"]),
                        "date_registered": int(row["date_registered"]),
                        "cert_time_to_live": int(row["cert_time_to_live"]),
                    }
                )

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--env", required=True)
    args = parser.parse_args()
    load_test_data(args.env)