from enum import Enum

from enums.user_role import UserRole
from ui_config import USER_PASSWORDS

class User(Enum):
    ROOT_ADMIN = ("root_admin@gmail.com", "root_admin", UserRole.ROOT_ADMIN)
    ADMIN = ("admin@gmail.com", "admin", UserRole.ADMIN)
    TRAIL_MANAGER = ("trail_manager@gmail.com", "trail_manager", UserRole.TRAIL_MANAGER)
    USER = ("user@gmail.com", "user", UserRole.USER)

    def __init__(self, email, username, role):
        self.email = email
        self.username = username
        self.role = role
        self.password = self.get_password()

    def get_password(self):
        return USER_PASSWORDS

    def __str__(self):
        return self.username