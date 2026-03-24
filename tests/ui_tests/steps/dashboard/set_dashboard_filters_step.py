from selenium import webdriver
from pages.dashboard_page import DashboardPage
from dtos.dashboard_filter_dto import DashboardFilterDTO

class SetDashboardFiltersStep:
    def __init__(self, driver: webdriver.Chrome, dashboard_filters: DashboardFilterDTO):
        self.driver = driver
        self.dashboard_filters = dashboard_filters

    def run(self):
        po = DashboardPage(self.driver)
        po.set_dashboard_filters(self.dashboard_filters)