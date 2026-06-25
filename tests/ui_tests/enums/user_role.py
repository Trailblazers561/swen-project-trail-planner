from enum import Enum

class UserRole(Enum):
    ROOT_ADMIN = "Root"
    ADMIN = "Admin"
    TRAIL_MANAGER = "Manager"
    USER = "User"
    GUEST = "Guest"