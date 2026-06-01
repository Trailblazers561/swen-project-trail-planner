from selenium import webdriver

from dtos.area_dto import AreaDTO
from pages.dashboard_page import DashboardPage
from pages.modals.edit_area_page import EditAreaPage

class RetrieveEditAreaAreasStep:
    """
    Retrievs List of Areas That Appears In Edit Areas Modal
    """
    def __init__(self, driver: webdriver.Chrome):
        self.driver = driver
        self.areas: list[AreaDTO] = []

    def run(self):
        po = DashboardPage(self.driver)
        po.click_edit_area()

        po = EditAreaPage(self.driver)
        self.areas = po.retrieve_area_options()
        po.close_modal()