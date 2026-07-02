import csv
from datetime import datetime, timedelta
from zoneinfo import ZoneInfo
from pathlib import Path

# NOTE: Data is unsorted, ensure the sort manually in each test, please don't change these values
DEVICE_DATA: list[dict[str, object]] = [] # ["id": int, "name": str, "notes": str, "date_manufactured": int]
TRAIL_DATA: list[dict[str, object]] = [] # ["id": int, "name": str, "latitude": float, "longitude": float, "notes": str, "date_activated": int]
DEVICE_TRAIL_DATA: list[dict[str, object]] = [] # ["id": int, "device_id": int, "trail_id": int, "notes": str, "date_installed": int]
AREA_DATA: list[dict[str, object]] = [] # ["name": str, "trail_id_list": [int]]
HOUR_LOG_DATA: list[dict[str, object]] = [] # ["device_trail_id": int, "start": int, "count": int]
DAY_LOG_DATA: list[dict[str, object]] = [] # ["device_trail_id": int, "start": int, "count": int]
WEEK_LOG_DATA: list[dict[str, object]] = [] # ["device_trail_id": int, "start": int, "count": int]
MONTH_LOG_DATA: list[dict[str, object]] = [] # ["device_trail_id": int, "start": int, "count": int]
DEVICE_LOG_DATA: list[dict[str, object]] = [] # ["device_id": int, "time": int, "count": int, "battery": int, "firmware_version": str, "rssi": int, "rsrp": int, "rsrq": int]

with open(Path(__file__).parent / "../../sample_data/devices.csv") as f:
    reader = csv.DictReader(f)
    for row in reader:
        DEVICE_DATA.append({
            "id": int(row["id"]),
            "name": row["name"],
            "notes": row["notes"],
            "date_manufactured": int(row["date_manufactured"])
        })
with open(Path(__file__).parent / "../../sample_data/test_devices.csv") as f:
    reader = csv.DictReader(f)
    for row in reader:
        DEVICE_DATA.append({
            "id": int(row["id"]),
            "name": row["name"],
            "notes": row["notes"],
            "date_manufactured": int(row["date_manufactured"])
        })

with open(Path(__file__).parent / "../../sample_data/trails.csv") as f:
    reader = csv.DictReader(f)
    for row in reader:
        TRAIL_DATA.append({
            "id": int(row["id"]),
            "name": row["name"],
            "notes": row["notes"],
            "latitude": float(row["latitude"]),
            "longitude": float(row["longitude"]),
            "date_activated": int(row["date_activated"])
        })
with open(Path(__file__).parent / "../../sample_data/test_trails.csv") as f:
    reader = csv.DictReader(f)
    for row in reader:
        TRAIL_DATA.append({
            "id": int(row["id"]),
            "name": row["name"],
            "notes": row["notes"],
            "latitude": float(row["latitude"]),
            "longitude": float(row["longitude"]),
            "date_activated": int(row["date_activated"])
        })

with open(Path(__file__).parent / "../../sample_data/device_trails.csv") as f:
    reader = csv.DictReader(f)
    for row in reader:
        DEVICE_TRAIL_DATA.append({
            "id": int(row["id"]),
            "device_id": int(row["device_id"]),
            "trail_id": int(row["trail_id"]),
            "notes": row["notes"],
            "date_installed": int(row["date_installed"])
        })
with open(Path(__file__).parent / "../../sample_data/test_device_trails.csv") as f:
    reader = csv.DictReader(f)
    for row in reader:
        DEVICE_TRAIL_DATA.append({
            "id": int(row["id"]),
            "device_id": int(row["device_id"]),
            "trail_id": int(row["trail_id"]),
            "notes": row["notes"],
            "date_installed": int(row["date_installed"])
        })

with open(Path(__file__).parent / "../../sample_data/areas.csv") as f:
    areas = {}
    reader = csv.DictReader(f)
    for row in reader:
        trail_id = int(row["trail_id"])
        area_name = row["name"]
        if areas.get(area_name):
            areas[area_name].append(trail_id)
        else:
            areas[area_name] = [trail_id]
    AREA_DATA.extend(areas.values())
with open(Path(__file__).parent / "../../sample_data/test_areas.csv") as f:
    areas = {}
    reader = csv.DictReader(f)
    for row in reader:
        trail_id = int(row["trail_id"])
        area_name = row["name"]
        if areas.get(area_name):
            areas[area_name].append(trail_id)
        else:
            areas[area_name] = [trail_id]
    AREA_DATA.extend(areas.values())

with open(Path(__file__).parent / "../../sample_data/hour_logs.csv") as f:
    reader = csv.DictReader(f)
    for row in reader:
        HOUR_LOG_DATA.append({
            "device_trail_id": int(row["device_trail_id"]),
            "start": int(row["start"]),
            "count": int(row["count"])
        })

with open(Path(__file__).parent / "../../sample_data/day_logs.csv") as f:
    reader = csv.DictReader(f)
    for row in reader:
        DAY_LOG_DATA.append({
            "device_trail_id": int(row["device_trail_id"]),
            "start": int(row["start"]),
            "count": int(row["count"])
        })
with open(Path(__file__).parent / "../../sample_data/days_recent.csv") as f:
    reader = csv.DictReader(f)
    current_midnight = datetime.now().astimezone(ZoneInfo("America/New_York")).replace(hour=0, minute=0, second=0, microsecond=0)
    for row in reader:
        DAY_LOG_DATA.append({
            "device_trail_id": int(row["device_trail_id"]),
            "start": int((current_midnight - timedelta(days=int(row["days_ago"]))).timestamp()),
            "count": int(row["count"])
        })

with open(Path(__file__).parent / "../../sample_data/week_logs.csv") as f:
    reader = csv.DictReader(f)
    for row in reader:
        WEEK_LOG_DATA.append({
            "device_trail_id": int(row["device_trail_id"]),
            "start": int(row["start"]),
            "count": int(row["count"])
        })

with open(Path(__file__).parent / "../../sample_data/month_logs.csv") as f:
    reader = csv.DictReader(f)
    for row in reader:
        MONTH_LOG_DATA.append({
            "device_trail_id": int(row["device_trail_id"]),
            "start": int(row["start"]),
            "count": int(row["count"])
        })

with open(Path(__file__).parent / "../../sample_data/device_logs.csv") as f:
    reader = csv.DictReader(f)
    for row in reader:
        DAY_LOG_DATA.append({
            "device_id": int(row["device_id"]),
            "time": int(row["time"]),
            "count": int(row["count"]),
            "battery": int(row["battery"]),
            "firmware_version": row["firmware_version"],
            "rssi": int(row["rssi"]),
            "rsrp": int(row["rsrp"]),
            "rsrq": int(row["rsrq"]),
        })
with open(Path(__file__).parent / "../../sample_data/logs_recent.csv") as f:
    reader = csv.DictReader(f)
    current_midnight = datetime.now().astimezone(ZoneInfo("America/New_York")).replace(hour=0, minute=0, second=0, microsecond=0)
    for row in reader:
        DAY_LOG_DATA.append({
            "device_id": int(row["device_id"]),
            "time": int((current_midnight - timedelta(days=int(row["days_ago"]))).timestamp()),
            "count": int(row["count"]),
            "battery": int(row["battery"]),
            "firmware_version": row["firmware_version"],
            "rssi": int(row["rssi"]),
            "rsrp": int(row["rsrp"]),
            "rsrq": int(row["rsrq"]),
        })