from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium_helper import SeleniumHelper as SH

from dtos.trail_dto import TrailDTO
from dtos.trail_group_dto import TrailGroupDTO

class EditTrailGroupPage:
    root = (By.XPATH, "//div[@data-testid='edit-trail-group-modal']")
    # Edit
    group_select = (By.XPATH, "//select[@id='group-select']")
    # Edit & Add
    group_name_input = (By.XPATH, "//input[@id='group-name']")
    create_update_group_button = (By.XPATH, "//button[@data-testid='confirm-button']")
    select_trail_checkbox_xpath = "//input[@data-testid='checkbox {}']"

    def __init__(self, driver: webdriver.Chrome):
        self.driver = driver
        SH.wait_for_element_appear(self.driver, self.root)

    def select_group(self, group_name: str):
        SH.select_dropdown_option(group_name)

    def set_group_information(self, group: TrailGroupDTO):
        if group.group_name:
            self._set_group_name(self, group.group_name)
        if group.trails:
            self._select_trails(group.trails)
    
    def create_update_group(self):
        SH.click_element(self.driver, self.create_update_group_button)

    def _set_group_name(self, group_name: str):
        SH.enter_text_to_element(self.driver, self.group_name_input, group_name)

    def _select_trails(self, trails: set[TrailDTO]):
        for trail in trails:
            trail_locator = (By.XPATH, self.select_trail_checkbox_xpath.format(trail))
            if not SH.retrieve_checkbox_selected(self.driver, trail_locator):
                SH.click_element(self.driver, trail_locator)