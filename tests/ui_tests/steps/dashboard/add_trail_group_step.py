from selenium import webdriver

from dtos.trail_group_dto import TrailGroupDTO
from pages.dashboard_page import DashboardPage
from pages.modals.edit_trail_group_page import EditTrailGroupPage

class AddTrailGroupStep:
    def __init__(self, driver: webdriver.Chrome, trail_group: TrailGroupDTO):
        self.driver = driver
        self.trail_group = trail_group

    def run(self):
        po = DashboardPage(self.driver)
        po.click_add_trail()

        po = EditTrailGroupPage(self.driver)
        po.set_group_information(self.trail_group)
        po.create_update_group()