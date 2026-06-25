import pytest_check
from enums.user_enum import User
from enums.user_role import UserRole

class UserDTO:
    def __init__(self, name: str="", password: str="",  email: str="", role: UserRole=None, user: User = None):
        if user == None:
            self.name = name
            self.password = password
            self.email = email
            self.role = role
        else:
            self.name = user.username
            self.password = user.password
            self.email = user.email
            self.role = user.role

    def __str__(self):
        return f"UserDTO [email={self.email}, password={self.password}, name={self.name}, role={self.role}]"

    def __repr__(self):
        return str(self)

    def __eq__(self, other):
        if not isinstance(other, UserDTO):
            return False
        other: UserDTO = other
        return self.email == other.email and self.password == other.password

    def compare(self, other):
        if not pytest_check.is_instance(other, UserDTO):
            return
        other: UserDTO = other

        pytest_check.equal(self.name, other.name)
        pytest_check.equal(self.password, other.password)