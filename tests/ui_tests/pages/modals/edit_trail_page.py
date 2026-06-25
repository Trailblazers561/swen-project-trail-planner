from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium_helper import SeleniumHelper as SH
from selenium.common.exceptions import NoSuchElementException

import re

from dtos.trail_dto import TrailDTO

class EditTrailPage:
    """
    Add / Edit Trail Modal From Dashboard
    """
    root = (By.XPATH, "//div[@data-testid='edit-trail-modal']")
    # Edit
    trail_select = (By.XPATH, "//select[@id='trail-select']")
    delete_trail_button = (By.XPATH, "//button[@data-testid='delete-button']")
    confirm_delete_button = (By.XPATH, "//button[@data-testid='confirm-delete']")
    cancel_delete_button = (By.XPATH, "//button[@data-testid='cancel-delete']")
    # Edit & Add
    trail_name_input = (By.XPATH, "//input[@id='trail-name']")
    area_select = (By.XPATH, "//select[@id='area']")
    create_update_trail_button = (By.XPATH, "//button[@data-testid='confirm-button']")
    close_button = (By.XPATH, "//button[@data-testid='modal-close']")

    def __init__(self, driver: webdriver.Chrome):
        self.driver = driver
        SH.wait_for_element_appear(self.driver, self.root)

    def select_trail(self, trail_name: str):
        options = SH.retrieve_dropdown_options(self.driver, self.trail_select)
        correct_option = None
        for option in options:
            if re.fullmatch(rf"{re.escape(trail_name)} \(ID: \d+\)", option):
                correct_option = option
                break
        if correct_option == None:
            raise NoSuchElementException(f"Cannot find option with trail_name [{trail_name}]")
        SH.select_dropdown_option(self.driver, self.trail_select, correct_option)

    def set_trail_information(self, trail: TrailDTO):
        if trail.name:
            self._set_trail_name(trail.name)
        if trail.area_name:
            self._set_area(trail.area_name)

    def delete_trail(self, confirm=True):
        SH.click_element(self.driver, self.delete_trail_button)
        SH.wait_for_element_appear(self.driver, self.confirm_delete_button)
        if confirm:
            SH.click_element(self.driver, self.confirm_delete_button)
            SH.wait_for_element_disappear(self.driver, self.root)
            SH.wait(.5)
        else:
            SH.click_element(self.driver, self.cancel_delete_button)

    def create_update_trail(self):
        SH.click_element(self.driver, self.create_update_trail_button)
        SH.wait_for_element_disappear(self.driver, self.root)
        SH.wait(.5)

    def _set_trail_name(self, name: str):
        SH.enter_text_to_element(self.driver, self.trail_name_input, name)

    def _set_area(self, area: str):
        SH.select_dropdown_option(self.driver, self.area_select, area)

    def retrieve_trail_options(self) -> list[TrailDTO]:
        options = SH.retrieve_dropdown_options(self.driver, self.trail_select)[1:] #Skip Select a trail
        return [TrailDTO(re.match(r"^(?P<name>.*?) \(ID: (?P<id>[0-9]+?)\)$", option).group("name")) for option in options]

    def close_modal(self) -> None:
        SH.click_element(self.driver, self.close_button)
        SH.wait_for_element_disappear(self.driver, self.root)