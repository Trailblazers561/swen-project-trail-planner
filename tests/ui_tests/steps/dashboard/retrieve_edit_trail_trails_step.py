from selenium import webdriver

from dtos.trail_dto import TrailDTO
from pages.dashboard_page import DashboardPage
from pages.modals.edit_trail_page import EditTrailPage

class RetrieveEditTrailTrailsStep:
    """
    Retrieves List of Trails That Appears In Edit Trail Modal
    """
    def __init__(self, driver: webdriver.Chrome):
        self.driver = driver
        self.trails: list[TrailDTO] = []

    def run(self):
        po = DashboardPage(self.driver)
        po.click_edit_trail()

        po = EditTrailPage(self.driver)
        self.trails = po.retrieve_trail_options()
        po.close_modal()