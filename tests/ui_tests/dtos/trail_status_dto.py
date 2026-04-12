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

    def __repr__(self):
        return str(self)

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

# EXPECTED_TRAIL_STATUSES: list[TrailStatusDTO] = []
# EXPECTED_TRAIL_STATUSES.append(TrailStatusDTO("Mt. Marcy", count, "98%", last_updated))
# EXPECTED_TRAIL_STATUSES.append(TrailStatusDTO("Giant Mountain", count, "89%", last_updated))
# EXPECTED_TRAIL_STATUSES.append(TrailStatusDTO("Poke-O-Moonshine Ranger Trail", count, "100%", last_updated))
# EXPECTED_TRAIL_STATUSES.append(TrailStatusDTO("Mt. Skylight", count, "85%", last_updated))
# EXPECTED_TRAIL_STATUSES.append(TrailStatusDTO("Cat Mountain", count, "60%", last_updated))
# EXPECTED_TRAIL_STATUSES.append(TrailStatusDTO("Bald Peak", count, "70%", last_updated))
# EXPECTED_TRAIL_STATUSES.append(TrailStatusDTO("Mt. Haystack", count, "99%", last_updated))
# EXPECTED_TRAIL_STATUSES.append(TrailStatusDTO("Beaver Meadow Trail", count, "94%", last_updated))
# EXPECTED_TRAIL_STATUSES.append(TrailStatusDTO("Mud Lake", count, "51%", last_updated))
# EXPECTED_TRAIL_STATUSES.append(TrailStatusDTO("Blueberry Trail", count, "62%", last_updated))