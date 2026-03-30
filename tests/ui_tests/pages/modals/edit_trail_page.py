from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium_helper import SeleniumHelper as SH

import re
from selenium.common.exceptions import NoSuchElementException

from dtos.trail_dto import TrailDTO

class EditTrailPage:
    root = (By.XPATH, "//div[@data-testid='edit-trail-modal']")
    # Edit
    trail_select = (By.XPATH, "//select[@id='trail-select']")
    delete_trail_button = (By.XPATH, "//button[@data-testid='delete-button']")
    confirm_delete_button = (By.XPATH, "//button[@data-testid='confirm-delete']")
    cancel_delete_button = (By.XPATH, "//button[@data-testid='cancel-delete']")
    # Edit & Add
    trail_name_input = (By.XPATH, "//input[@id='trail-name']")
    trail_group_select = (By.XPATH, "//select[@id='trail-group']")
    create_update_trail_button = (By.XPATH, "//button[@data-testid='confirm-button']")

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
        if trail.trail_name:
            self._set_trail_name(trail.trail_name)
        if trail.trail_group:
            self._set_trail_group(trail.trail_group)

    def delete_trail(self, confirm=True):
        SH.click_element(self.driver, self.delete_trail_button)
        SH.wait_for_element_appear(self.driver, self.confirm_delete_button)
        if confirm:
            SH.click_element(self.driver, self.confirm_delete_button)
        else:
            SH.click_element(self.driver, self.cancel_delete_button)

    def create_update_trail(self):
        SH.click_element(self.driver, self.create_update_trail_button)

    def _set_trail_name(self, name: str):
        SH.enter_text_to_element(self.driver, self.trail_name_input, name)

    def _set_trail_group(self, group: str):
        SH.select_dropdown_option(self.driver, self.trail_group_select, group)