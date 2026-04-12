from selenium import webdriver
from pages.dashboard_page import DashboardPage
from dtos.trail_dto import TrailDTO
from dtos.trail_group_dto import TrailGroupDTO
from enums.granularity import Granularity

class RetrieveDashboardOptionsStep:
    def __init__(self, driver: webdriver.Chrome):
        self.driver = driver
        self.granularities: list[Granularity] = []
        self.trails: list[TrailDTO] = []
        self.trail_groups: list[TrailGroupDTO] = []

    def run(self):
        po = DashboardPage(self.driver)
        self.granularities = po.retrieve_granularity_options()
        self.trails = po.retrieve_trail_options()
        self.trail_groups = po.retrieve_trail_group_options()