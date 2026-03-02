from selenium import webdriver
from dtos.user_dto import UserDTO
from pages.login_page import LoginPage

class LoginStep:
    def __init__(self, driver: webdriver.Chrome, user: UserDTO, alert: bool = False):
        self.driver = driver
        self.user = user
        self.alert = alert
        self.alert_text: str

    def run(self):
        po = LoginPage(self.driver)
        self.alert_text = po.sign_in(self.user, self.alert)