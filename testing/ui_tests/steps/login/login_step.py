from selenium import webdriver

from dtos.user_dto import UserDTO
from enums.login_mode import LoginMode
from pages.login_page import LoginPage

class LoginStep:
    """
    Logs Into Application
    """
    def __init__(self, driver: webdriver.Chrome, user: UserDTO, login_mode: LoginMode = LoginMode.NORMAL, username_login=True):
        self.driver = driver
        self.user = user
        self.login_mode = login_mode
        self.username_login = username_login
        self.alert_validation_text: str

    def run(self):
        po = LoginPage(self.driver)
        self.alert_validation_text = po.sign_in(self.user, self.login_mode, self.username_login)