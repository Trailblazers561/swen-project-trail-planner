from selenium import webdriver

from dtos.trail_group_dto import TrailGroupDTO
from pages.dashboard_page import DashboardPage
from pages.modals.edit_trail_group_page import EditTrailGroupPage

class RetrieveEditTrailGroupGroupsStep:
    """
    Retrievs List of Trail Groups That Appears In Edit Trail Groups Modal
    """
    def __init__(self, driver: webdriver.Chrome):
        self.driver = driver
        self.trail_groups: list[TrailGroupDTO] = []

    def run(self):
        po = DashboardPage(self.driver)
        po.click_edit_trail_group()

        po = EditTrailGroupPage(self.driver)
        self.trail_groups = po.retrieve_trail_group_options()
        po.close_modal()