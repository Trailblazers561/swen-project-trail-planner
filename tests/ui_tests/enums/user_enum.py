from enum import Enum

class User(Enum):
    ROOT_ADMIN = ("root_admin@gmail.com", "root_admin")
    ADMIN = ("admin@gmail.com", "admin")
    TRAIL_MANAGER = ("trail_manager@gmail.com", "trail_manager")
    USER = ("user@gmail.com", "user")

    def __init__(self, email, username):
        self.email = email
        self.username = username
        self.password = self.get_password()

    def get_password(self):
        return "password" # can be updated to retrieve secretly when needed

    def __str__(self):
        return self.username