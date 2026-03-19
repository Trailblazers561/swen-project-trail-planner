from selenium import webdriver

from pages.navbar_page import NavbarPage
from enums.user_action import UserAction

class PerformUserActionStep:
    def __init__(self, driver: webdriver.Chrome, user_action: UserAction):
        self.driver = driver
        self.user_action = user_action

    def run(self):
        po = NavbarPage(self.driver)
        po.perform_user_action(self.user_action)