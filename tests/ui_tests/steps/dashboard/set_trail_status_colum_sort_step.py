from selenium import webdriver

from enums.trail_status_column import TrailStatusColumn
from pages.dashboard_page import DashboardPage

class SetTrailStatusColumnSort:
    """
    Sorts A Trail Status Column Header
    """
    def __init__(self, driver: webdriver.Chrome, column: TrailStatusColumn, ascending: bool):
        self.driver = driver
        self.column = column
        self.ascending = ascending

    def run(self):
        po = DashboardPage(self.driver)
        po.set_trail_status_column_sort(self.column, self.ascending)