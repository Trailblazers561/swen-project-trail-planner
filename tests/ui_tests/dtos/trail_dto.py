import pytest_check

class TrailDTO:
    def __init__(self, trail_name: str, trail_id: int=None):
        self.trail_name = trail_name
        self.trail_id = trail_id

    def __str__(self):
        return f"TrailDTO [trail_name={self.trail_name}, trail_id={self.trail_id}]"

    def __eq__(self, other):
        if not isinstance(other, TrailDTO):
            return False
        other: TrailDTO = other

        if (self.trail_id != None) and (other.trail_id != None):
            return self.trail_name == other.trail_name and self.trail_id == other.trail_id
        return self.trail_name == other.trail_name

    def __hash__(self):
        if self.trail_id is not None:
            return hash((self.trail_id, self.trail_name))
        return hash(self.trail_name)

    def compare(self, other):
        if not pytest_check.is_instance(other, TrailDTO):
            return
        other: TrailDTO = other

        pytest_check.equal(self.trail_name, other.trail_name)
        if (self.trail_id != None) and (other.trail_id != None):
            pytest_check.equal(self.trail_id, other.trail_id)