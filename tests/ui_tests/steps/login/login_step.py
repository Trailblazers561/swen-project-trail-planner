from selenium import webdriver
from ui_tests.dtos.user_dto import UserDTO
from ui_tests.pages.login_page import LoginPage
from ui_tests.enums.login_mode import LoginMode

class LoginStep:
    def __init__(self, driver: webdriver.Chrome, user: UserDTO, login_mode: LoginMode = LoginMode.NORMAL):
        self.driver = driver
        self.user = user
        self.login_mode = login_mode
        self.alert_validation_text: str

    def run(self):
        po = LoginPage(self.driver)
        self.alert_validation_text = po.sign_in(self.user, self.login_mode)