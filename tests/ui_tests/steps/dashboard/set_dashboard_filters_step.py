from selenium import webdriver

from dtos.dashboard_filter_dto import DashboardFilterDTO
from pages.dashboard_page import DashboardPage

class SetDashboardFiltersStep:
    def __init__(self, driver: webdriver.Chrome, dashboard_filters: DashboardFilterDTO):
        self.driver = driver
        self.dashboard_filters = dashboard_filters

    def run(self):
        po = DashboardPage(self.driver)
        po.set_dashboard_filters(self.dashboard_filters)