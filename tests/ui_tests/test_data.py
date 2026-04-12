import csv
from datetime import datetime, timedelta
from zoneinfo import ZoneInfo
from pathlib import Path
from dtos.trail_dto import TrailDTO
from dtos.trail_group_dto import TrailGroupDTO
from dtos.graph_dto import GraphDTO, LineDTO, PointDTO
from enums.granularity import Granularity

TRAILS: dict[int, TrailDTO] = {}
TRAIL_GROUPS: list[TrailGroupDTO] = []
DEVICE_TRAILS: dict[int, TrailDTO] = {}
HOUR_DATA: dict[TrailDTO, dict[str, int]] = {}
DAY_DATA: dict[TrailDTO, dict[str, int]] = {}
WEEK_DATA: dict[TrailDTO, dict[str, int]] = {}
MONTH_DATA: dict[TrailDTO, dict[str, int]] = {}
YEAR_DATA: dict[TrailDTO, dict[str, int]] = {}
def retrieve_graph(start: datetime, end: datetime, granularity: Granularity, trail_ids: list) -> GraphDTO:
    ...

with open(Path(__file__).parent / "../../sampledata/trails.csv") as f:
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

with open(Path(__file__).parent / "../../sampledata/trail_groups.csv") as f:
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

with open(Path(__file__).parent / "../../sampledata/device_trails.csv") as f:
    reader = csv.DictReader(f)
    for row in reader:
        DEVICE_TRAILS[int(row["id"])] = TRAILS[int(row["trail_id"])]

with open(Path(__file__).parent / "../../sampledata/hours.csv") as f:
    reader = csv.DictReader(f)
    for row in reader:
        trail = DEVICE_TRAILS[int(row["device_trail_id"])]
        if not HOUR_DATA.get(trail):
            HOUR_DATA[trail] = []
        HOUR_DATA[trail].append({"start": int(row["start"]), "count": int(row["count"])})

with open(Path(__file__).parent / "../../sampledata/days.csv") as f:
    reader = csv.DictReader(f)
    for row in reader:
        trail = DEVICE_TRAILS[int(row["device_trail_id"])]
        if not DAY_DATA.get(trail):
            DAY_DATA[trail] = []
        DAY_DATA[trail].append({"start": int(row["start"]), "count": int(row["count"]), "battery": int(row["battery"])})

with open(Path(__file__).parent / "../../sampledata/weeks.csv") as f:
    reader = csv.DictReader(f)
    for row in reader:
        trail = DEVICE_TRAILS[int(row["device_trail_id"])]
        if not WEEK_DATA.get(trail):
            WEEK_DATA[trail] = []
        WEEK_DATA[trail].append({"start": int(row["start"]), "count": int(row["count"]), "battery": int(row["battery"])})

with open(Path(__file__).parent / "../../sampledata/months.csv") as f:
    reader = csv.DictReader(f)
    for row in reader:
        trail = DEVICE_TRAILS[int(row["device_trail_id"])]
        if not MONTH_DATA.get(trail):
            MONTH_DATA[trail] = []
        MONTH_DATA[trail].append({"start": int(row["start"]), "count": int(row["count"]), "battery": int(row["battery"])})

for trail, datas in MONTH_DATA.items():
    YEAR_DATA[trail] = []
    current_year = datetime.fromtimestamp(datas[0]["start"]).year
    YEAR_DATA[trail].append({"start": int(datetime(current_year-3, 1, 1).timestamp()), "count": 0, "battery": 100})
    YEAR_DATA[trail].append({"start": int(datetime(current_year-2, 1, 1).timestamp()), "count": 0, "battery": 100})
    YEAR_DATA[trail].append({"start": int(datetime(current_year-1, 1, 1).timestamp()), "count": 0, "battery": 100})
    year_data = {"start": int(datetime(current_year, 1, 1).timestamp()), "count": 0, "battery": 100}
    for data in datas:
        data_year = datetime.fromtimestamp(data["start"]).year
        if current_year == data_year:
            year_data["count"] += data["count"]
            year_data["battery"] = data["battery"]
        else:
            YEAR_DATA[trail].append(year_data)
            year_data = {"start": int(datetime(data_year, 1, 1).timestamp()), "count": data["count"], "battery": data["battery"]}
    YEAR_DATA[trail].append(year_data)
    
    

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

    start = start.astimezone(ZoneInfo("America/New_York")).replace(hour=0, minute=0, second=0, microsecond=0)
    end = end.astimezone(ZoneInfo("America/New_York")).replace(hour=0, minute=0, second=0, microsecond=0) + timedelta(minutes=1)

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

    a1 = datetime.fromtimestamp(partial_start_timestamp)
    a2 = datetime.fromtimestamp(partial_end_timestamp)
    a3 = datetime.fromtimestamp(regular_start_timestamp)
    a4 = datetime.fromtimestamp(regular_end_timestamp)




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