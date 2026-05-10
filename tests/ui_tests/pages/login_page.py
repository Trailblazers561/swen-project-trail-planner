from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium_helper import SeleniumHelper as SH

from dtos.user_dto import UserDTO
from enums.login_mode import LoginMode

class LoginPage:
    """
    Login / Registration Page (/login)
    """
    root = (By.XPATH, "//div[@id='loginForm']")
    email_input = (By.XPATH, "//input[@data-testid='username-input']")
    password_input = (By.XPATH, "//input[@data-testid='password-input']")
    sign_in_button = (By.XPATH, "//button[@data-testid='login-button']")
    sign_in_error = (By.XPATH, "//div[@data-testid='sign-in-error']//p")

    def __init__(self, driver: webdriver.Chrome):
        self.driver = driver
        SH.wait_for_element_appear(self.driver, self.root)

    def sign_in(self, user: UserDTO, login_mode: LoginMode, username_login: bool) -> str:
        if username_login:
            self._enter_username(user.name)
        else:
            self._enter_username(user.email)
        self._enter_password(user.password)
        self._click_sign_in()
        if login_mode == LoginMode.NORMAL:
            SH.wait_for_element_disappear(self.driver, self.root, 30)
        elif login_mode == LoginMode.ALERT:
            SH.wait(.5)
            return self._retrieve_alert()
        elif login_mode == LoginMode.VALIDATION:
            return self._retrieve_validation()

    def _enter_username(self, email: str) -> None:
        SH.enter_text_to_element(self.driver, self.email_input, email)

    def _enter_password(self, password: str) -> None:
        SH.enter_text_to_element(self.driver, self.password_input, password)

    def _click_sign_in(self) -> None:
        SH.click_element(self.driver, self.sign_in_button)

    def _dismiss_alert(self) -> str:
        return SH.dismiss_alert(self.driver)

    def _retrieve_alert(self) -> str:
        return SH.retrieve_text_from_element(self.driver, self.sign_in_error)

    def _retrieve_validation(self) -> str:
        return SH.retrieve_element_attribute(self.driver, self.email_input, "validationMessage") \
                or SH.retrieve_element_attribute(self.driver, self.password_input, "validationMessage")