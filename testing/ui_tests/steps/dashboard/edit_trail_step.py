from selenium import webdriver

from dtos.trail_dto import TrailDTO
from pages.dashboard_page import DashboardPage
from pages.modals.edit_trail_page import EditTrailPage

class EditTrailStep:
    """
    Edits A Trail With The Given Criteria
    """
    def __init__(self, driver: webdriver.Chrome, trail: TrailDTO, old_trail_name: str="", delete: bool=False):
        self.driver = driver
        self.trail = trail
        if old_trail_name:
            self.old_trail_name = old_trail_name
        else:
            self.old_trail_name = trail.name
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