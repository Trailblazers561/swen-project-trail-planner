from selenium import webdriver
from selenium_helper import SeleniumHelper as SH

class LogoutStep:
    def __init__(self, driver: webdriver.Chrome):
        self.driver = driver

    def run(self):
        pass