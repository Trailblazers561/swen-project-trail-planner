from selenium import webdriver
from pages.dashboard_page import DashboardPage

class ImportDataStep:
    def __init__(self, driver: webdriver.Chrome):
        self.driver = driver

    def run(self):
        po = DashboardPage(self.driver)
        po.click_import_data()
        # TODO: import