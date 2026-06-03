from selenium import webdriver

from dtos.area_dto import AreaDTO
from pages.dashboard_page import DashboardPage
from pages.modals.edit_area_page import EditAreaPage

class AddAreaStep:
    """
    Adds an Area
    """
    def __init__(self, driver: webdriver.Chrome, area: AreaDTO):
        self.driver = driver
        self.area = area

    def run(self):
        po = DashboardPage(self.driver)
        po.click_add_trail()

        po = EditAreaPage(self.driver)
        po.set_area_information(self.area)
        po.create_update_area()