from selenium import webdriver

from dtos.trail_dto import TrailDTO
from pages.dashboard_page import DashboardPage
from pages.modals.edit_trail_page import EditTrailPage

class AddTrailStep:
    def __init__(self, driver: webdriver.Chrome, trail: TrailDTO):
        self.driver = driver
        self.trail = trail

    def run(self):
        po = DashboardPage(self.driver)
        po.click_add_trail()

        po = EditTrailPage(self.driver)
        po.set_trail_information(self.trail)
        po.create_update_trail()