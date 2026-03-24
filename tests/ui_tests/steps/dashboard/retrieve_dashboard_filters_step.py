from selenium import webdriver
from pages.dashboard_page import DashboardPage
from dtos.dashboard_filter_dto import DashboardFilterDTO

class RetrieveDashboardFiltersStep:
    def __init__(self, driver: webdriver.Chrome):
        self.driver = driver
        self.dashboard_filters: DashboardFilterDTO = None

    def run(self):
        po = DashboardPage(self.driver)
        self.dashboard_filters = po.retrieve_dashboard_filters()