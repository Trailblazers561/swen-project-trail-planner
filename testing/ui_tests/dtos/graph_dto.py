import pytest_check
from datetime import datetime

class PointDTO:
    def __init__(self, date: datetime, count: int):
        self.date = date
        self.count = count

    def __str__(self):
        return f"PointDTO [date={self.date}, count={self.count}]"

    def __repr__(self):
        return str(self)

    def __eq__(self, other):
        if not isinstance(other, PointDTO):
            return False
        other: PointDTO = other
        return self.date == other.date and self.count == other.count

    def __hash__(self):
        return hash((self.date, self.count))

class LineDTO:
    def __init__(self, trail_name: str, points: list[PointDTO]):
        self.trail_name = trail_name
        self.points = points

    def __str__(self):
        return f"LineDTO [trail_name={self.trail_name}, len(points)={len(self.points)}], points[0]={[self.points[0]]}, points[-1]={self.points[-1]}"

    def __repr__(self):
        return str(self)

    def __eq__(self, other):
        if not isinstance(other, LineDTO):
            return False
        other: LineDTO = other

        return self.trail_name == other.trail_name and self.points == other.points

    def __hash__(self):
        return hash((self.trail_name, frozenset(self.points)))

class GraphDTO:
    def __init__(self, title: str, lines: set[LineDTO]):
        self.title = title
        self.lines = lines

    def __str__(self):
        return f"GraphDTO [title={self.title}, lines={self.lines}]"

    def __repr__(self):
        return str(self)

    def __eq__(self, other):
        if not isinstance(other, GraphDTO):
            return False
        other: GraphDTO = other

        return self.title == other.title and self.lines == other.lines

    def compare(self, other):
        if not pytest_check.is_instance(other, GraphDTO):
            return
        other: GraphDTO = other

        pytest_check.equal(self.title, other.title)
        pytest_check.equal(self.lines, other.lines)

