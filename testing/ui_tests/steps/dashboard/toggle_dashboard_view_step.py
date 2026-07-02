from selenium import webdriver

from pages.dashboard_page import DashboardPage

class ToggleDashboardViewStep:
    """
    Toggles Dashboard View Between Graph and Trail Status Overview
    """
    def __init__(self, driver: webdriver.Chrome):
        self.driver = driver

    def run(self):
        po = DashboardPage(self.driver)
        po.click_toggle_view()