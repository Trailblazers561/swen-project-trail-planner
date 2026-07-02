from enum import Enum

class Granularity(Enum):
    HOUR = "Hourly"
    DAY = "Daily"
    WEEK = "Weekly"
    MONTH = "Monthly"
    YEAR = "Yearly"