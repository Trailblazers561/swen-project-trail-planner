from selenium import webdriver
from pages.logout_page import LogoutPage

class LogoutStep:
    def __init__(self, driver: webdriver.Chrome):
        self.driver = driver

    def run(self):
        po = LogoutPage(self.driver)
        po.logout()