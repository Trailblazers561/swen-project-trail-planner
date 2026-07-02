from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium_helper import SeleniumHelper as SH

import re

from dtos.trail_dto import TrailDTO
from dtos.area_dto import AreaDTO

class EditAreaPage:
    """
    Add / Edit A Modal From Dashboard
    """
    root = (By.XPATH, "//div[@data-testid='edit-area-modal']")
    # Edit
    area_select = (By.XPATH, "//select[@id='area-select']")
    # Edit & Add
    area_name_input = (By.XPATH, "//input[@id='area-name']")
    create_update_area_button = (By.XPATH, "//button[@data-testid='confirm-button']")
    select_trail_checkbox_xpath = "//input[@data-testid='checkbox {}']"
    close_button = (By.XPATH, "//button[@data-testid='modal-close']")

    def __init__(self, driver: webdriver.Chrome):
        self.driver = driver
        SH.wait_for_element_appear(self.driver, self.root)

    def select_area(self, area_name: str):
        SH.select_dropdown_option(area_name)
        SH.wait(1)

    def set_area_information(self, area: AreaDTO):
        if area.name:
            self._set_area_name(self, area.name)
        if area.trails:
            self._select_trails(area.trails)
    
    def create_update_area(self):
        SH.click_element(self.driver, self.create_update_area_button)

    def _set_area_name(self, area_name: str):
        SH.enter_text_to_element(self.driver, self.area_name_input, area_name)

    def _select_trails(self, trails: set[TrailDTO]):
        for trail in trails:
            trail_locator = (By.XPATH, self.select_trail_checkbox_xpath.format(trail))
            if not SH.retrieve_checkbox_selected(self.driver, trail_locator):
                SH.click_element(self.driver, trail_locator)

    def retrieve_area_options(self) -> list[AreaDTO]:
        options = SH.retrieve_dropdown_options(self.driver, self.area_select)[1:] #Skip Select an area
        return [AreaDTO(re.match(r"^(?P<name>.*?) \((?P<trails>[0-9]+?) trails?\)$", option).group("name")) for option in options]

    def close_modal(self) -> None:
        SH.click_element(self.driver, self.close_button)