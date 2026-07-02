from selenium import webdriver
from selenium_helper import SeleniumHelper as SH

class DismissAlertStep:
    """
    Dismisses A Popup Alert And Retrieves Alert Text
    """
    def __init__(self, driver: webdriver.Chrome):
        self.driver = driver
        self.alert_text = ""

    def run(self):
        self.alert_text = SH.dismiss_alert(self.driver)