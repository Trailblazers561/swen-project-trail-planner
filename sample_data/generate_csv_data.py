
import csv
import random
from pathlib import Path
from datetime import datetime, timedelta, timezone
from zoneinfo import ZoneInfo

# This file is designed to generate csv data that gets loaded for testing. If the csv's already exist, no need to run this code.

# Hiker Multiplier based on day of the week Monday - Sunday
weekday_modifier = {0: .8, 1: .65, 2: .50, 3: .60, 4: .90, 5: 1.95, 6: 1.6}
hour_modifier = [m / 24 for m in [0.23, 0.18, 0.12, 0.12, 0.18, 0.47, 0.94, 1.40, 1.64, 1.40, 1.29, 1.17, 1.05, 1.05, 1.17, 1.40, 1.76, 2.11, 1.87, 1.52, 1.17, 0.82, 0.59, 0.35, 0.28]]

trails = {
    "Mt. Marcy": [90, 20],
    "Giant Mountain": [50, 12],
    "Poke-O-Moonshine Ranger Trail": [40, 10],
    "Mt. Skylight": [35, 9],
    "Cat Mountain": [30, 8],
    "Bald Peak": [25, 6],
    "Beaver Meadow Trail": [20, 5],
    "Mt. Haystack": [20, 7],
    "Mud Lake": [15, 5],
    "Blueberry Trail": [15, 8]
}

trail_ids = {
    "Mt. Marcy": 1,
    "Giant Mountain": 2,
    "Poke-O-Moonshine Ranger Trail": 3,
    "Mt. Skylight": 4,
    "Cat Mountain": 5,
    "Bald Peak": 6,
    "Beaver Meadow Trail": 7,
    "Mt. Haystack": 8,
    "Mud Lake": 9,
    "Blueberry Trail": 10
}

hour_data = []
full_hour_data = []
day_data = []

# Generate Day and Hour Data
for trail, stats in trails.items():
    current_day = datetime.fromisoformat("2026-01-01").replace(tzinfo=ZoneInfo("America/New_York"))
    end_day = datetime.fromisoformat("2026-03-31").replace(tzinfo=ZoneInfo("America/New_York"))
    # Cutoff regular hour to avoid having to load unessicary data, but keep the full data in a csv for later use
    hour_end_day = datetime.fromisoformat("2026-01-03").replace(tzinfo=ZoneInfo("America/New_York"))
    battery = 100
    device_trail_id = trail_ids[trail]
    while (current_day <= end_day):
        if (battery > 1 and random.random() < 1/3):
            battery = battery - 1
        hikers = max(int(random.normalvariate(*stats) * (sum(weekday_modifier.values()) / 7)), 0)
        today_start_utc = current_day.astimezone(timezone.utc)
        tomorrow_start_utc = (current_day + timedelta(days=1)).astimezone(timezone.utc)
        today_hours = int((tomorrow_start_utc - today_start_utc).total_seconds() / 3600)

        counts  = [int(hikers * m) + (random.random() < (hikers * m % 1)) for m in hour_modifier[:today_hours]]
        hikers = sum(counts)
        hour_timestamp = current_day.timestamp()
        for count in counts:
            # Appending battery onto data so that tests don't have to manually calculate it
            if (current_day <= hour_end_day):
                hour_data.append([device_trail_id, int(hour_timestamp), count, battery])
            full_hour_data.append([device_trail_id, int(hour_timestamp), count, battery])
            hour_timestamp += 60 * 60

        day_data.append([device_trail_id, int(current_day.timestamp()), hikers, battery])

        current_day += timedelta(days=1)

# Generate week data from adding day data
week_data = []
weeks = {}

for device_trail_id, start, count, battery in day_data:
    day_date = datetime.fromtimestamp(start)
    key = (device_trail_id, int((day_date - timedelta(days=day_date.weekday())).timestamp()))
    if not weeks.get(key):
        weeks[key] = [device_trail_id, key[1], 0, battery]
    weeks[key][2] += count
    weeks[key][3] = battery

week_data.extend(weeks.values())
week_data.sort(key=lambda x: (x[0], x[1]))

# Generate month data from adding day data
month_data = []
months = {}

for device_trail_id, start, count, battery in day_data:
    day_date = datetime.fromtimestamp(start)
    key = (device_trail_id, int((day_date.replace(day=1)).timestamp()))
    if not months.get(key):
        months[key] = [device_trail_id, key[1], 0, battery]
    months[key][2] += count
    months[key][3] = battery

month_data.extend(months.values())
month_data.sort(key=lambda x: (x[0], x[1]))

# Write data to csv files
with open(Path(__file__).parent / "hour_data.csv", "w", newline='') as f:
    file = csv.writer(f)
    file.writerow(["device_trail_id", "start", "count", "battery"])
    for data in hour_data:
        file.writerow(data)

with open(Path(__file__).parent / "full_hour_data.csv", "w", newline='') as f:
    file = csv.writer(f)
    file.writerow(["device_trail_id", "start", "count", "battery"])
    for data in full_hour_data:
        file.writerow(data)

with open(Path(__file__).parent / "day_data.csv", "w", newline='') as f:
    file = csv.writer(f)
    file.writerow(["device_trail_id", "start", "count", "battery"])
    for data in day_data:
        file.writerow(data)

with open(Path(__file__).parent / "week_data.csv", "w", newline='') as f:
    file = csv.writer(f)
    file.writerow(["device_trail_id", "start", "count", "battery"])
    for data in week_data:
        file.writerow(data)

with open(Path(__file__).parent / "month_data.csv", "w", newline='') as f:
    file = csv.writer(f)
    file.writerow(["device_trail_id", "start", "count", "battery"])
    for data in month_data:
        file.writerow(data)