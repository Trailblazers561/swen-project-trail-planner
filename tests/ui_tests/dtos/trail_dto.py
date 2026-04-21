import pytest_check
from datetime import datetime

class TrailDTO:
    def __init__(self, name: str, id: int=None, trail_group_name: str="", notes: str="", latitude: float=0, longitude: float=0, date_activated: datetime=None, date_retired: datetime=None):
        self.name = name
        self.id = id
        self.trail_group_name = trail_group_name
        self.notes = notes
        self.latitude = latitude
        self.longitude = longitude
        self.date_activated = date_activated
        self.date_retired = date_retired

    def __str__(self):
        return f"TrailDTO [name={self.name}, id={self.id}, trail_group_name={self.trail_group_name}, notes={self.notes}, latitude={self.latitude}, longitude={self.longitude}, date_activated={self.date_activated}, date_retired={self.date_retired}]"

    def __repr__(self):
        return str(self)

    def __eq__(self, other):
        if not isinstance(other, TrailDTO):
            return False
        other: TrailDTO = other

        return self.name == other.name

    def __hash__(self):
        return hash(self.name)

    def compare(self, other):
        if not pytest_check.is_instance(other, TrailDTO):
            return
        other: TrailDTO = other

        pytest_check.equal(self.name, other.name)
        if (self.id != None) and (other.id != None):
            pytest_check.equal(self.id, other.id)
        if (self.trail_group_name != "") and (other.trail_group_name != ""):
            pytest_check.equal(self.trail_group_name, other.trail_group_name)
        if (self.notes != "") and (other.notes != ""):
            pytest_check.equal(self.notes, other.notes)
        if (self.latitude != 0) and (other.latitude != 0):
            pytest_check.equal(self.latitude, other.latitude)
        if (self.longitude != 0) and (other.longitude != 0):
            pytest_check.equal(self.longitude, other.longitude)
        if (self.date_activated != None) and (other.date_activated != None):
            pytest_check.equal(self.date_activated, other.date_activated)
        if (self.date_retired != None) and (other.date_retired != None):
            pytest_check.equal(self.date_retired, other.date_retired)