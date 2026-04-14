import csv
from datetime import datetime, timedelta
from zoneinfo import ZoneInfo
from pathlib import Path
from dtos.trail_dto import TrailDTO
from dtos.trail_group_dto import TrailGroupDTO
from dtos.graph_dto import GraphDTO, LineDTO, PointDTO
from enums.granularity import Granularity
from enums.trail_status_column import TrailStatusColumn
from dtos.trail_status_dto import TrailStatusDTO
from dtos.device_dto import DeviceDTO

TRAILS: dict[int, TrailDTO] = {}
DEVICES: dict[int, DeviceDTO] = {}
TRAIL_GROUPS: list[TrailGroupDTO] = []
DEVICE_TRAIL_TRAILS: dict[int, TrailDTO] = {}
DEVICE_TRAIL_DEVICES: dict[int, DeviceDTO] = {}
DEVICE_TO_TRAIL: dict[int, TrailDTO] = {}
HOUR_DATA: dict[TrailDTO, dict[str, int]] = {}
DAY_DATA: dict[TrailDTO, dict[str, int]] = {}
WEEK_DATA: dict[TrailDTO, dict[str, int]] = {}
MONTH_DATA: dict[TrailDTO, dict[str, int]] = {}
YEAR_DATA: dict[TrailDTO, dict[str, int]] = {}
RECENT_DATA: dict[TrailDTO, dict[str, int]] = {}
TRAIL_STATUSES: list[TrailStatusDTO] = []
def retrieve_graph(start: datetime, end: datetime, granularity: Granularity, trail_ids: list) -> GraphDTO:
    ...
def retrieve_trail_status_overview(column: TrailStatusColumn=TrailStatusColumn.TRAIL_NAME, reverse: bool=False) -> list[TrailStatusDTO]:
    ...
def retrieve_csv_list(start: datetime, end: datetime, granularity: Granularity, trail_ids: list) -> list[dict[str, str]]:
    ...

with open(Path(__file__).parent / "../../sample_data/trails.csv") as f:
    reader = csv.DictReader(f)
    for row in reader:
        trail = TrailDTO(
            id=int(row["id"]),
            name=row["name"],
            notes=row["notes"],
            latitude=float(row["latitude"]),
            longitude=float(row["longitude"]),
            date_activated=(datetime.fromtimestamp(int(row["date_activated"])))
        )
        TRAILS[trail.id] = trail
with open(Path(__file__).parent / "../../sample_data/test_trails.csv") as f:
    reader = csv.DictReader(f)
    for row in reader:
        trail = TrailDTO(
            id=int(row["id"]),
            name=row["name"],
            notes=row["notes"],
            latitude=float(row["latitude"]),
            longitude=float(row["longitude"]),
            date_activated=(datetime.fromtimestamp(int(row["date_activated"])))
        )
        TRAILS[trail.id] = trail

with open(Path(__file__).parent / "../../sample_data/trail_groups.csv") as f:
    groups = {}
    reader = csv.DictReader(f)
    for row in reader:
        trail_id = int(row["trail_id"])
        group_name = row["name"]
        TRAILS[trail_id].trail_group_name = group_name
        if groups.get(group_name):
            groups[group_name].trails.add(TRAILS[trail_id])
        else:
            groups[group_name] = TrailGroupDTO(group_name, {TRAILS[trail_id]})
    TRAIL_GROUPS = list(groups.values())
with open(Path(__file__).parent / "../../sample_data/test_trail_groups.csv") as f:
    groups = {}
    reader = csv.DictReader(f)
    for row in reader:
        trail_id = int(row["trail_id"])
        group_name = row["name"]
        TRAILS[trail_id].trail_group_name = group_name
        if groups.get(group_name):
            groups[group_name].trails.add(TRAILS[trail_id])
        else:
            groups[group_name] = TrailGroupDTO(group_name, {TRAILS[trail_id]})
    TRAIL_GROUPS.extend(groups.values())

with open(Path(__file__).parent / "../../sample_data/devices.csv") as f:
    reader = csv.DictReader(f)
    for row in reader:
        device = DeviceDTO(
            id=int(row["id"])
        )
        DEVICES[device.id] = device
with open(Path(__file__).parent / "../../sample_data/test_devices.csv") as f:
    reader = csv.DictReader(f)
    for row in reader:
        device = DeviceDTO(
            id=int(row["id"])
        )
        DEVICES[device.id] = device

with open(Path(__file__).parent / "../../sample_data/device_trails.csv") as f:
    reader = csv.DictReader(f)
    for row in reader:
        DEVICE_TRAIL_TRAILS[int(row["id"])] = TRAILS[int(row["trail_id"])]
        DEVICE_TO_TRAIL[int(row["device_id"])] = TRAILS[int(row["trail_id"])]
        DEVICE_TRAIL_DEVICES[int(row["id"])] = DEVICES[int(row["device_id"])]
        DEVICES[int(row["device_id"])].current_trail = TRAILS[int(row["trail_id"])]
with open(Path(__file__).parent / "../../sample_data/test_device_trails.csv") as f:
    reader = csv.DictReader(f)
    for row in reader:
        DEVICE_TRAIL_TRAILS[int(row["id"])] = TRAILS[int(row["trail_id"])]
        DEVICE_TO_TRAIL[int(row["device_id"])] = TRAILS[int(row["trail_id"])]
        DEVICE_TRAIL_DEVICES[int(row["id"])] = DEVICES[int(row["device_id"])]
        DEVICES[int(row["device_id"])].current_trail = TRAILS[int(row["trail_id"])]

with open(Path(__file__).parent / "../../sample_data/hours.csv") as f:
    reader = csv.DictReader(f)
    for row in reader:
        trail = DEVICE_TRAIL_TRAILS[int(row["device_trail_id"])]
        if not HOUR_DATA.get(trail):
            HOUR_DATA[trail] = []
        HOUR_DATA[trail].append({"start": int(row["start"]), "count": int(row["count"]), "battery": f"{int(row['battery'])}%", "recorded": True})

with open(Path(__file__).parent / "../../sample_data/days.csv") as f:
    reader = csv.DictReader(f)
    for row in reader:
        trail = DEVICE_TRAIL_TRAILS[int(row["device_trail_id"])]
        if not DAY_DATA.get(trail):
            DAY_DATA[trail] = []
        DAY_DATA[trail].append({"start": int(row["start"]), "count": int(row["count"]), "battery": f"{int(row['battery'])}%", "recorded": True})

with open(Path(__file__).parent / "../../sample_data/weeks.csv") as f:
    reader = csv.DictReader(f)
    for row in reader:
        trail = DEVICE_TRAIL_TRAILS[int(row["device_trail_id"])]
        if not WEEK_DATA.get(trail):
            WEEK_DATA[trail] = []
        WEEK_DATA[trail].append({"start": int(row["start"]), "count": int(row["count"]), "battery": f"{int(row['battery'])}%", "recorded": True})

with open(Path(__file__).parent / "../../sample_data/months.csv") as f:
    reader = csv.DictReader(f)
    for row in reader:
        trail = DEVICE_TRAIL_TRAILS[int(row["device_trail_id"])]
        if not MONTH_DATA.get(trail):
            MONTH_DATA[trail] = []
        MONTH_DATA[trail].append({"start": int(row["start"]), "count": int(row["count"]), "battery": f"{int(row['battery'])}%", "recorded": True})

for trail, datas in MONTH_DATA.items():
    YEAR_DATA[trail] = []
    current_year = datetime.fromtimestamp(datas[0]["start"]).year
    YEAR_DATA[trail].append({"start": int(datetime(current_year-3, 1, 1).timestamp()), "count": 0, "battery": "100%", "recorded": False})
    YEAR_DATA[trail].append({"start": int(datetime(current_year-2, 1, 1).timestamp()), "count": 0, "battery": "100%", "recorded": False})
    YEAR_DATA[trail].append({"start": int(datetime(current_year-1, 1, 1).timestamp()), "count": 0, "battery": "100%", "recorded": False})
    year_data = {"start": int(datetime(current_year, 1, 1).timestamp()), "count": 0, "battery": "100%", "recorded": True}
    for data in datas:
        data_year = datetime.fromtimestamp(data["start"]).year
        if current_year == data_year:
            year_data["count"] += data["count"]
            year_data["battery"] = data["battery"]
        else:
            YEAR_DATA[trail].append(year_data)
            year_data = {"start": int(datetime(data_year, 1, 1).timestamp()), "count": data["count"], "battery": data["battery"], "recorded": True}
    YEAR_DATA[trail].append(year_data)

with open(Path(__file__).parent / "../../sample_data/days_recent.csv") as f:
    reader = csv.DictReader(f)
    current_midnight = datetime.now().astimezone(ZoneInfo("America/New_York")).replace(hour=0, minute=0, second=0, microsecond=0)
    for row in reader:
        trail = DEVICE_TRAIL_TRAILS[int(row["device_trail_id"])]
        if not RECENT_DATA.get(trail):
            RECENT_DATA[trail] = []
        RECENT_DATA[trail].append({"start": int((current_midnight - timedelta(days=int(row["days_ago"]))).timestamp()), "count": int(row["count"]), "battery": f"{int(row['battery'])}%", "recorded": True})
        DEVICE_TRAIL_DEVICES[int(row["device_trail_id"])].battery = f"{int(row['battery'])}%"

for trail in TRAILS.values():
    status = RECENT_DATA.get(trail, [])
    weekly_count = sum(day["count"] for day in status) if status else 0
    battery_status = status[-1]["battery"]  if status else ""
    last_updated = datetime.fromtimestamp(status[-1]["start"]).replace(hour=0) if status else None

    TRAIL_STATUSES.append(TrailStatusDTO(trail.name, weekly_count, battery_status, last_updated))

def retrieve_graph(start: datetime, end: datetime, granularity: Granularity, trail_ids: list) -> GraphDTO:
    DATA = {}
    if granularity == Granularity.HOUR:
        DATA = HOUR_DATA
    elif granularity == Granularity.DAY:
        DATA = DAY_DATA
    elif granularity == Granularity.WEEK:
        DATA = WEEK_DATA
    elif granularity == Granularity.MONTH:
        DATA = MONTH_DATA
    elif granularity == Granularity.YEAR:
        DATA = YEAR_DATA
    else:
        raise ValueError("Invalid granularity")

    start = start.replace(tzinfo=ZoneInfo("America/New_York"), hour=0, minute=0, second=0, microsecond=0)
    end = end.replace(tzinfo=ZoneInfo("America/New_York"), hour=0, minute=0, second=0, microsecond=0) + timedelta(minutes=1)

    if granularity in {Granularity.HOUR, Granularity.DAY}:
        regular_start_timestamp = int(start.timestamp())
        regular_end_timestamp = int(end.timestamp())
    else:
        partial_start_timestamp = int(start.timestamp())
        partial_end_timestamp = int(end.timestamp())
        if granularity == Granularity.WEEK:
            regular_start_timestamp = int((start + timedelta(days=(7 - start.weekday()) % 7)).timestamp())
            regular_end_timestamp = int((end - timedelta(days=end.weekday(), minutes=1)).timestamp())
        if granularity in {Granularity.MONTH, Granularity.YEAR}:
            regular_start_timestamp = int((start if start.day == 1 else (start.replace(day=28) + timedelta(days=4)).replace(day=1)).timestamp())
            regular_end_timestamp = int((end.replace(day=1) - timedelta(minutes=1)).timestamp())

    lines = {}
    for trail_id in trail_ids:
        lines[trail_id] = {
            PointDTO(datetime.fromtimestamp(log["start"]).astimezone(ZoneInfo("America/New_York")), log["count"]) for log in DATA[TRAILS[trail_id]]
            if regular_start_timestamp <= log["start"] < regular_end_timestamp
        }

    if granularity in {Granularity.WEEK, Granularity.MONTH, Granularity.YEAR} and partial_start_timestamp <= regular_start_timestamp:
        for trail_id in trail_ids:
            lines[trail_id].add(PointDTO(start, sum(log["count"] for log in DAY_DATA[TRAILS[trail_id]] if partial_start_timestamp <= log["start"] < regular_start_timestamp)))

    if granularity in {Granularity.WEEK, Granularity.MONTH, Granularity.YEAR} and partial_end_timestamp >= regular_end_timestamp:
        for trail_id in trail_ids:
            lines[trail_id].add(PointDTO(datetime.fromtimestamp(regular_end_timestamp).astimezone(ZoneInfo("America/New_York")), sum(log["count"] for log in DAY_DATA[TRAILS[trail_id]] if regular_end_timestamp <= log["start"] < partial_end_timestamp)))

    graph_lines = {LineDTO(TRAILS[trail_id].name, points) for trail_id, points in lines.items()}

    if not len(trail_ids):
        graph_title = "No Trails Selected"
    elif len(trail_ids) == len(TRAILS):
        graph_title = f"All Trails from {start.month}/{start.day}/{start.year} to {end.month}/{end.day}/{end.year}"
    elif len(trail_ids) == 1:
        graph_title = f"{TRAILS[trail_ids[0]].name} from {start.month}/{start.day}/{start.year} to {end.month}/{end.day}/{end.year}"
    elif len(trail_ids) == 2:
        graph_title = f"{TRAILS[trail_ids[0]].name} & {TRAILS[trail_ids[1]].name} from {start.month}/{start.day}/{start.year} to {end.month}/{end.day}/{end.year}"
    else:
        graph_title = f"{len(trail_ids)} Trails from {start.month}/{start.day}/{start.year} to {end.month}/{end.day}/{end.year}"

    return GraphDTO(graph_title, graph_lines)

def retrieve_trail_status_overview(column: TrailStatusColumn=TrailStatusColumn.TRAIL_NAME, reverse: bool=False) -> list[TrailStatusDTO]:
    if column == TrailStatusColumn.TRAIL_NAME:
        return sorted(TRAIL_STATUSES, key=lambda ts: ts.trail_name, reverse=reverse)
    elif column == TrailStatusColumn.WEEKLY_COUNT:
        return sorted(sorted(TRAIL_STATUSES, key=lambda ts: ts.trail_name), key=lambda ts: ts.weekly_count, reverse=reverse)
    elif column == TrailStatusColumn.BATTERY_STATUS:
        return sorted(sorted(TRAIL_STATUSES, key=lambda ts: ts.trail_name), key=lambda ts: ts.battery_status, reverse=reverse)
    elif column == TrailStatusColumn.LAST_UPDATED:
        return sorted(sorted(TRAIL_STATUSES, key=lambda ts: ts.trail_name), key=lambda ts: (ts.last_updated is not None, ts.last_updated), reverse=reverse)
    raise ValueError("Invalid column")

def retrieve_csv_list(start: datetime, end: datetime, granularity: Granularity, trail_ids: list) -> list[dict[str, str]]:
    DATA = {}
    if granularity == Granularity.HOUR:
        DATA = HOUR_DATA
    elif granularity == Granularity.DAY:
        DATA = DAY_DATA
    elif granularity == Granularity.WEEK:
        DATA = WEEK_DATA
    elif granularity == Granularity.MONTH:
        DATA = MONTH_DATA
    elif granularity == Granularity.YEAR:
        DATA = YEAR_DATA
    else:
        raise ValueError("Invalid granularity")

    if granularity == Granularity.HOUR:
        start = start.replace(tzinfo=ZoneInfo("America/New_York"), minute=0, second=0, microsecond=0)
        end = end.replace(tzinfo=ZoneInfo("America/New_York"), minute=0, second=0, microsecond=0)
    else:
        start = start.replace(tzinfo=ZoneInfo("America/New_York"), hour=0, minute=0, second=0, microsecond=0)
        end = end.replace(tzinfo=ZoneInfo("America/New_York"), hour=0, minute=0, second=0, microsecond=0)

    rows = []
    for trail_id in trail_ids:
        rows.extend([{
            "Trail ID": str(trail_id),
            "Trail Name": TRAILS[trail_id].name,
            "Start Time": datetime.fromtimestamp(log["start"]).astimezone(ZoneInfo("America/New_York")).strftime(f"%Y/%m/%d{' %I:%M %p' if granularity == Granularity.HOUR else ''}"),
            f"{granularity.value} Count": str(log["count"]),
            "Battery %": log["battery"][:-1]
        } for log in DATA[TRAILS[trail_id]] if start.timestamp() <= log["start"] <= end.timestamp() and log["recorded"]])
    rows.sort(key=lambda row: (int(row["Trail ID"]), datetime.strptime(row["Start Time"], f"%Y/%m/%d{' %I:%M %p' if granularity == Granularity.HOUR else ''}")))

    return rows
retrieve_graph(datetime.fromisoformat("2024-01-01"), datetime.fromisoformat("2026-01-01"), Granularity.YEAR, [2, 3])