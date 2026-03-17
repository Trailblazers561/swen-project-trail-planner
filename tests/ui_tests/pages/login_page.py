from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium_helper import SeleniumHelper as SH

from  dtos.user_dto import UserDTO
from enums.login_mode import LoginMode

class LoginPage:
    root = (By.XPATH, "//div[@class='loginForm']")
    email_input = (By.XPATH, "//input[@id='email']")
    password_input = (By.XPATH, "//input[@id='password']")
    sign_in_button = (By.XPATH, "//button[@id='signInButton']")

    def __init__(self, driver: webdriver.Chrome):
        self.driver = driver
        SH.wait_for_element_appear(self.driver, self.root)

    def sign_in(self, user: UserDTO, login_mode: LoginMode) -> str:
        self._enter_email(user.email)
        self._enter_password(user.password)
        self._click_sign_in()
        if login_mode == LoginMode.NORMAL:
            SH.wait_for_element_disappear(self.driver, self.root)
        elif login_mode == LoginMode.ALERT:
            SH.wait(.5)
            return self._dismiss_alert()
        elif login_mode == LoginMode.VALIDATION:
            return self._retrieve_validation()

    def _enter_email(self, email: str) -> None:
        SH.enter_text_to_element(self.driver, self.email_input, email)

    def _enter_password(self, password: str) -> None:
        SH.enter_text_to_element(self.driver, self.password_input, password)

    def _click_sign_in(self) -> None:
        SH.click_element(self.driver, self.sign_in_button)

    def _dismiss_alert(self) -> str:
        return SH.dismiss_alert(self.driver)

    def _retrieve_validation(self) -> str:
        return SH.retrieve_element_attribute(self.driver, self.email_input, "validationMessage") \
                or SH.retrieve_element_attribute(self.driver, self.password_input, "validationMessage")