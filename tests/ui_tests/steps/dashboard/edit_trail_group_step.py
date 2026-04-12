from selenium import webdriver
from pages.dashboard_page import DashboardPage
from dtos.trail_group_dto import TrailGroupDTO
from pages.modals.edit_trail_group_page import EditTrailGroupPage

class EditTrailGroupStep:
    def __init__(self, driver: webdriver.Chrome, trail_group: TrailGroupDTO, old_group_name: str=""):
        self.driver = driver
        self.trail_group = trail_group
        if old_group_name:
            self.old_group_name = old_group_name
        else:
            old_group_name = trail_group.name

    def run(self):
        po = DashboardPage(self.driver)
        po.click_edit_trail_group()

        po = EditTrailGroupPage(self.driver)
        po.select_group(self.old_group_name)
        po.set_group_information(self.trail_group)
        po.create_update_group()