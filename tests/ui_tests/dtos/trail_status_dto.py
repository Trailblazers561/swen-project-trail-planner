import pytest_check
from datetime import datetime

class TrailStatusDTO:
    def __init__(self, trail_name: str, weekly_count: int, battery_status: str, last_updated: datetime):
        self.trail_name = trail_name
        self.weekly_count = weekly_count
        self.battery_status = battery_status
        self.last_updated = last_updated

    def __str__(self):
        return f"TrailStatusDTO [trail_name={self.trail_name}, weekly_count={self.weekly_count}, battery_status={self.battery_status}, last_updated={self.last_updated}]"

    def __eq__(self, other):
        if not isinstance(other, TrailStatusDTO):
            return False
        other: TrailStatusDTO = other

        return self.trail_name == other.trail_name and self.weekly_count == other.weekly_count \
            and self.battery_status == other.battery_status and self.last_updated == other.last_updated

    def compare(self, other):
        if not pytest_check.is_instance(other, TrailStatusDTO):
            return
        other: TrailStatusDTO = other

        pytest_check.equal(self.trail_name, other.trail_name)
        pytest_check.equal(self.weekly_count, other.weekly_count)
        pytest_check.equal(self.battery_status, other.battery_status)
        pytest_check.equal(self.last_updated, other.last_updated)