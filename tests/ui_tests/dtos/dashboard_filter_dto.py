import pytest_check
from datetime import datetime

from dtos.trail_dto import TrailDTO
from dtos.trail_group_dto import TrailGroupDTO

class DashboardFilterDTO:
    def __init__(self, date_start: datetime=None, date_end: datetime=None, trails: set[TrailDTO]=set(), trail_groups: set[TrailGroupDTO]=set()):
        self.date_start = date_start
        self.date_end = date_end
        self.trails = trails
        self.trail_groups = trail_groups

    def __str__(self):
        return f"DashboardFilterDTO [date_start={self.date_start}, date_end={self.date_end}, trails={self.trails}, trail_groups={self.trail_groups}]"

    def __eq__(self, other):
        if not isinstance(other, DashboardFilterDTO):
            return False
        other: DashboardFilterDTO = other

        return self.date_start == other.date_start and self.date_end == other.date_end and self.trails == other.trails and self.trail_groups == other.trail_groups

    def compare(self, other):
        if not pytest_check.is_instance(other, DashboardFilterDTO):
            return
        other: DashboardFilterDTO = other

        pytest_check.equal(self.date_start, other.date_start)
        pytest_check.equal(self.date_end, other.date_end)
        pytest_check.equal(self.trails, other.trails)
        pytest_check.equal(self.trail_groups, other.trail_groups)