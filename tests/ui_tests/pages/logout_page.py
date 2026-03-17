from selenium import webdriver
from selenium.webdriver.common.by import By
from ui_tests.selenium_helper import SeleniumHelper as SH

# This page exists for the sole purpose of login_test, but will be removed when the header stuff is implemented
class LogoutPage:
    root = (By.XPATH, "//button[@class='logout-button']")

    def __init__(self, driver: webdriver.Chrome):
        self.driver = driver
        SH.wait_for_element_appear(self.driver, self.root)

    def logout(self) -> None:
        SH.click_element(self.driver, self.root)