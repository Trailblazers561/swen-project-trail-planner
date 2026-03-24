from selenium import webdriver
from pages.dashboard_page import DashboardPage
from dtos.trail_status_dto import TrailStatusDTO

class RetrueveTrailStatusStep:
    def __init__(self, driver: webdriver.Chrome):
        self.driver = driver
        self.trail_status: TrailStatusDTO = None

    def run(self):
        po = DashboardPage(self.driver)
        self.trail_status = po.retrieve_trail_status()