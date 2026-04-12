import pytest_check

from dtos.trail_dto import TrailDTO

class TrailGroupDTO:
    def __init__(self, name: str, trails: set[TrailDTO]=set()):
        self.name = name
        self.trails = trails

    def __str__(self):
        return f"TrailGroupDTO [name={self.name}, trail_id={self.trails}]"

    def __repr__(self):
        return str(self)

    def __eq__(self, other):
        if not isinstance(other, TrailGroupDTO):
            return False
        other: TrailGroupDTO = other

        return self.name == other.name and self.trails == other.trails

    def __hash__(self):
        return hash((self.name, frozenset(self.trails)))

    def compare(self, other):
        if not pytest_check.is_instance(other, TrailGroupDTO):
            return
        other: TrailGroupDTO = other

        pytest_check.equal(self.name, other.name)
        pytest_check.equal(self.trails, other.trails)