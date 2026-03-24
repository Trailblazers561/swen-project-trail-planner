import pytest_check

from dtos.trail_dto import TrailDTO

class TrailGroupDTO:
    def __init__(self, group_name: str, trails: set[TrailDTO]=set()):
        self.group_name = group_name
        self.trails = trails

    def __str__(self):
        return f"TrailGroupDTO [group_name={self.group_name}, trail_id={self.trails}]"

    def __eq__(self, other):
        if not isinstance(other, TrailGroupDTO):
            return False
        other: TrailGroupDTO = other

        return self.group_name == other.group_name and self.trails == other.trails

    def __hash__(self):
        return hash((self.group_name, frozenset(self.trails)))

    def compare(self, other):
        if not pytest_check.is_instance(other, TrailGroupDTO):
            return
        other: TrailGroupDTO = other

        pytest_check.equal(self.group_name, other.group_name)
        pytest_check.equal(self.trails, other.trails)