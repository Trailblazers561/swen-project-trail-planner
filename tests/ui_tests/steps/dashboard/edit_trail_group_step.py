from selenium import webdriver
from pages.dashboard_page import DashboardPage

class EditTrailGroupStep:
    def __init__(self, driver: webdriver.Chrome):
        self.driver = driver

    def run(self):
        po = DashboardPage(self.driver)
        po.click_edit_trail_group()
        # TODO: Fill out modal