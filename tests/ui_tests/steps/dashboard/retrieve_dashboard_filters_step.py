from selenium import webdriver

from dtos.dashboard_filter_dto import DashboardFilterDTO
from pages.dashboard_page import DashboardPage

class RetrieveDashboardFiltersStep:
    """
    Retrieves Currently Selected Dashboard Filters
    """
    def __init__(self, driver: webdriver.Chrome):
        self.driver = driver
        self.dashboard_filters: DashboardFilterDTO = None

    def run(self):
        po = DashboardPage(self.driver)
        self.dashboard_filters = po.retrieve_dashboard_filters()