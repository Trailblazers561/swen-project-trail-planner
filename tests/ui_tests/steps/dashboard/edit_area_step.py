from selenium import webdriver

from dtos.area_dto import AreaDTO
from pages.dashboard_page import DashboardPage
from pages.modals.edit_area_page import EditAreaPage

class EditAreaStep:
    """
    Edits an Area With the Given Criteria
    """
    def __init__(self, driver: webdriver.Chrome, area: AreaDTO, old_area_name: str=""):
        self.driver = driver
        self.area = area
        if old_area_name:
            self.old_area_name = old_area_name
        else:
            old_area_name = area.name

    def run(self):
        po = DashboardPage(self.driver)
        po.click_edit_area()

        po = EditAreaPage(self.driver)
        po.select_area(self.old_area_name)
        po.set_area_information(self.area)
        po.create_update_area()