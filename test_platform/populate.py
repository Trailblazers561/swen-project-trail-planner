#!/usr/bin/env python3
"""
Populate all trails with historical hiker data.

Trail configs and seasonality are loaded from trails.toml.

Daily traffic = summer_weekday_hikers × season_multiplier × dow_multiplier

Usage:
    export TRAIL_API_KEY="..."
    python3 populate.py                    # populate all trails
    python3 populate.py --dry-run          # preview without uploading
    python3 populate.py --start 2026-03-01 # override start date
    python3 populate.py --trails 1 2 3     # only these trail IDs
"""

import argparse
import random
import sys
import tomllib
from datetime import date, timedelta
from pathlib import Path
from types import SimpleNamespace

from emulator import run as emulator_run

CONFIG_FILE = Path(__file__).parent / "trails.toml"


def load_config() -> dict:
    with open(CONFIG_FILE, "rb") as f:
        return tomllib.load(f)


def _memorial_day(year: int) -> date:
    """Last Monday of May."""
    d = date(year, 5, 31)
    while d.weekday() != 0:
        d -= timedelta(days=1)
    return d


def _columbus_day(year: int) -> date:
    """Second Monday of October."""
    d = date(year, 10, 1)
    while d.weekday() != 0:
        d += timedelta(days=1)
    return d + timedelta(weeks=1)


def season_for_date(d: date) -> str:
    year = d.year
    if d < date(year, 3, 15):
        return "winter"
    elif d < _memorial_day(year):
        return "spring"
    elif d <= _columbus_day(year):
        return "summer"
    else:
        return "fall"


_DOW_NAMES = ["monday", "tuesday", "wednesday", "thursday", "friday", "saturday", "sunday"]


def generate_weather(start: date, end: date, config: dict) -> dict:
    """Return {date: multiplier} for every day in [start, end]. Same weather for all trails."""
    w = config["weather"]
    weather = {}
    d = start
    while d <= end:
        if random.random() < w["bad_day_probability"]:
            weather[d] = random.uniform(w["bad_day_min_multiplier"], w["bad_day_max_multiplier"])
        else:
            weather[d] = 1.0
        d += timedelta(days=1)
    return weather


def make_day_multiplier_fn(config: dict):
    """Return a function(date) -> float combining season and day-of-week multipliers."""
    season_mults = config["season_multipliers"]
    dow_list = [config["dow_multipliers"][name] for name in _DOW_NAMES]

    def multiplier(d: date) -> float:
        return season_mults[season_for_date(d)] * dow_list[d.weekday()]

    return multiplier


def generate_weather_seeded(start: date, end: date, config: dict, seed: int) -> dict:
    """Return {date: multiplier} using a fixed seed (for reproducible test trails)."""
    rng = random.Random(seed)
    w = config["weather"]
    weather = {}
    d = start
    while d <= end:
        if rng.random() < w["bad_day_probability"]:
            weather[d] = rng.uniform(w["bad_day_min_multiplier"], w["bad_day_max_multiplier"])
        else:
            weather[d] = 1.0
        d += timedelta(days=1)
    return weather


def main() -> None:
    config = load_config()
    trail_configs = config["trails"]

    parser = argparse.ArgumentParser(
        description="Populate trails with historical hiker data",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog=__doc__,
    )
    parser.add_argument("--start", metavar="YYYY-MM-DD", default="2026-01-01")
    parser.add_argument("--end", metavar="YYYY-MM-DD", default=None)
    parser.add_argument("--trails", metavar="N", type=int, nargs="+",
                        help="Only populate these trail IDs (default: all)")
    parser.add_argument("--areas", metavar="AREA", nargs="+",
                        help="Only populate trails in these areas (default: all)")
    parser.add_argument("--dry-run", action="store_true",
                        help="Print what would be sent without calling the API")
    args = parser.parse_args()

    configs = trail_configs
    if args.trails:
        configs = [t for t in trail_configs if t["id"] in args.trails]
        if not configs:
            sys.exit(f"No matching trail IDs found in {args.trails}")
    if args.areas:
        configs = [t for t in configs if t.get("area") in args.areas]
        if not configs:
            sys.exit(f"No trails found for areas: {args.areas}")

    if args.end is None:
        args.end = (date.today() - timedelta(days=1)).isoformat()

    start_date = date.fromisoformat(args.start)
    end_date = date.fromisoformat(args.end)

    day_multiplier_fn = make_day_multiplier_fn(config)
    # Shared weather for non-fixed-seed trails (same bad days across all real trails)
    shared_weather = generate_weather(start_date, end_date, config)
    bad_days = sum(1 for v in shared_weather.values() if v < 1.0)
    total_days = len(shared_weather)

    total_trails = len(configs)
    print(f"Populating {total_trails} trails: {args.start} → {args.end}")
    print(f"Shared weather: {bad_days}/{total_days} bad days ({100*bad_days//total_days}%)")
    print(f"Mode: {'DRY RUN' if args.dry_run else 'LIVE'}")
    print("=" * 60)

    for i, trail in enumerate(configs, 1):
        trail_id = trail["id"]
        base_hikers = trail["summer_weekday_hikers"]
        name = trail["name"]
        device_id = trail.get("device_id", f"robot-counter-{trail_id:02d}")
        zero_day_prob = trail.get("zero_day_probability", 0.0)
        fixed_seed = trail.get("fixed_seed")

        # Fixed-seed trails get their own deterministic weather so they're fully reproducible
        if fixed_seed is not None:
            weather = generate_weather_seeded(start_date, end_date, config, fixed_seed)
        else:
            weather = shared_weather

        print(f"\n[{i}/{total_trails}] {name} (ID {trail_id}, device {device_id}, {base_hikers}/day summer baseline)")
        trail_args = SimpleNamespace(
            device_id=device_id,
            trail_id=trail_id,
            hikers_per_day=base_hikers,
            day_multiplier_fn=day_multiplier_fn,
            weather_by_date=weather,
            zero_day_probability=zero_day_prob,
            fixed_seed=fixed_seed,
            start=args.start,
            end=args.end,
            days=None,
            dry_run=args.dry_run,
        )
        emulator_run(trail_args)

    print("=" * 60)
    print(f"All {total_trails} trails populated.")


if __name__ == "__main__":
    main()
