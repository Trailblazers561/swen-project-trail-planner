from selenium import webdriver

from dtos.trail_status_dto import TrailStatusDTO
from pages.dashboard_page import DashboardPage

class RetrieveTrailStatusesStep:
    """
    Retrievs List of Trail Statuses From Trail Status Overview
    """
    def __init__(self, driver: webdriver.Chrome, max: int=-1):
        self.driver = driver
        self.max = max
        self.trail_statuses: list[TrailStatusDTO] = []

    def run(self):
        po = DashboardPage(self.driver)
        self.trail_statuses = po.retrieve_trail_statuses(self.max)