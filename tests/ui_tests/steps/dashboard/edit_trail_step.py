from selenium import webdriver
from pages.dashboard_page import DashboardPage
from dtos.trail_dto import TrailDTO
from pages.modals.edit_trail_page import EditTrailPage

class EditTrailStep:
    def __init__(self, driver: webdriver.Chrome, trail: TrailDTO, old_trail_name: str="", delete: bool=False):
        self.driver = driver
        self.trail = trail
        if old_trail_name:
            self.old_trail_name = old_trail_name
        else:
            old_trail_name = trail.trail_name
        self.delete = delete

    def run(self):
        po = DashboardPage(self.driver)
        po.click_edit_trail()

        po = EditTrailPage(self.driver)
        po.select_trail(self.old_trail_name)
        po.set_trail_information(self.trail)
        if self.delete:
            po.delete_trail()
        else:
            po.create_update_trail()