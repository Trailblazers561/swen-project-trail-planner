from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium_helper import SeleniumHelper as SH

from enums.user_action import UserAction

class NavbarPage:
    root = (By.XPATH, "//nav[@id='navbar']")
    user_role = (By.XPATH, "//div[@id='user-role']")
    user_icon = (By.XPATH, "//button[@id='user-icon-button']")
    user_action_xpath = "//div[@id='user-icon-group']/div[@data-testid='{}']"

    def __init__(self, driver: webdriver.Chrome):
        self.driver = driver
        SH.wait_for_element_appear(self.driver, self.root)

    def get_user_role(self) -> str:
        return SH.retrieve_text_from_element(self.driver, self.user_role)

    def perform_user_action(self, user_action: UserAction) -> None:
        SH.click_element(self.driver, self.user_icon)
        SH.click_element(self.driver, (By.XPATH, self.user_action_xpath.format(user_action.value)))