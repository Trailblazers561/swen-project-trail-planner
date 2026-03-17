import pytest_check
from enums.user_enum import User

class UserDTO:
    def __init__(self, email: str="", password: str="", name: str="", user: User = None):
        if user == None:
            self.email = email
            self.password = password
            self.name = name
        else:
            self.email = user.email
            self.password = user.password
            self.name = user.name

    def __str__(self):
        return f"UserDTO [emal={self.email}, password={self.password}, name={self.name}]"

    def __eq__(self, other):
        if not isinstance(other, UserDTO):
            return
        other: UserDTO = other
        return self.email == other.email and self.password == other.password

    def compare(self, other):
        if not pytest_check.is_instance(other, UserDTO):
            return
        other: UserDTO = other

        pytest_check.equal(self.email, other.email)
        pytest_check.equal(self.password, other.password)