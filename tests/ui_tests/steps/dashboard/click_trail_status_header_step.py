from selenium import webdriver

from enums.trail_status_column import TrailStatusColumn
from pages.dashboard_page import DashboardPage

class ClickTrailStatusHeaderStep:
    """
    Clicks A Trail Status Header To Sort It
    """
    def __init__(self, driver: webdriver.Chrome, column: TrailStatusColumn):
        self.driver = driver
        self.column = column

    def run(self):
        po = DashboardPage(self.driver)
        po.click_trail_status_column(self.column)