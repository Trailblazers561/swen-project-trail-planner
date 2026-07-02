from selenium import webdriver

from dtos.trail_dto import TrailDTO
from dtos.area_dto import AreaDTO
from enums.granularity import Granularity
from pages.dashboard_page import DashboardPage

class RetrieveDashboardOptionsStep:
    """
    Retrievs List of Granularities, Trails, and Areas, That Appear On Dashboard Dropdowns
    """
    def __init__(self, driver: webdriver.Chrome):
        self.driver = driver
        self.granularities: list[Granularity] = []
        self.trails: list[TrailDTO] = []
        self.areas: list[AreaDTO] = []

    def run(self):
        po = DashboardPage(self.driver)
        self.granularities = po.retrieve_granularity_options()
        self.trails = po.retrieve_trail_options()
        self.areas = po.retrieve_area_options()