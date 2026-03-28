import pytest_check

from dtos.trail_dto import TrailDTO

class DeviceDTO:
    def __init__(self, device_id: str, current_trail: TrailDTO=None, battery: str = ""):
        self.device_id = device_id
        self.current_trail = current_trail
        self.battery = battery

    def __str__(self):
        return f"DeviceDTO [device_id={self.device_id}, current_trail={self.current_trail}, battery={self.battery}]"

    def __eq__(self, other):
        if not isinstance(other, DeviceDTO):
            return False
        other: DeviceDTO = other

        return self.device_id == other.device_id and self.current_trail == other.current_trail and self.battery == other.battery

    def __hash__(self):
        return hash(self.device_id)

    def compare(self, other):
        if not pytest_check.is_instance(other, DeviceDTO):
            return
        other: DeviceDTO = other

        pytest_check.equal(self.device_id, other.device_id)
        pytest_check.equal(self.current_trail, other.current_trail)
        pytest_check.equal(self.battery, other.battery)