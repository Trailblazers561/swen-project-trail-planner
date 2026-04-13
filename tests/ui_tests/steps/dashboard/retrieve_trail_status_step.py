from selenium import webdriver
from pages.dashboard_page import DashboardPage
from dtos.trail_status_dto import TrailStatusDTO

class RetrieveTrailStatusStep:
    def __init__(self, driver: webdriver.Chrome):
        self.driver = driver
        self.trail_status: list[TrailStatusDTO] = []

    def run(self):
        po = DashboardPage(self.driver)
        self.trail_status = po.retrieve_trail_status()