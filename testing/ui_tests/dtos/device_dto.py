import pytest_check

from dtos.trail_dto import TrailDTO

class DeviceDTO:
    def __init__(self, id: str, current_trail: TrailDTO=None, battery: str = ""):
        self.id = id
        self.current_trail = current_trail
        self.battery = battery

    def __str__(self):
        return f"DeviceDTO [id={self.id}, current_trail={self.current_trail}, battery={self.battery}]"

    def __repr__(self):
        return str(self)

    def __eq__(self, other):
        if not isinstance(other, DeviceDTO):
            return False
        other: DeviceDTO = other

        return self.id == other.id and self.current_trail == other.current_trail and self.battery == other.battery

    def __hash__(self):
        return hash(self.id)

    def compare(self, other):
        if not pytest_check.is_instance(other, DeviceDTO):
            return
        other: DeviceDTO = other

        pytest_check.equal(self.id, other.id)
        pytest_check.equal(self.current_trail, other.current_trail)
        pytest_check.equal(self.battery, other.battery)