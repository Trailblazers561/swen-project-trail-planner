import pytest
import pytest_check
from selenium_helper import SeleniumHelper as SH

from dtos.user_dto import UserDTO
from enums.user_enum import User
from steps.login.login_step import LoginStep
from steps.login.logout_step import LogoutStep
from enums.login_mode import LoginMode

@pytest.mark.UI
def login_test():
    driver = SH.get_driver()

    try:
        # Test Logging In With Correct Users
        users = [
            # UserDTO(user=User.ROOT_ADMIN),
            UserDTO(user=User.ADMIN),
            # UserDTO(user=User.TRAIL_MANAGER),
            # UserDTO(user=User.USER)
        ]

        for user in users:
            user_login_logout(driver, user)

        # Test Validation Popups Appaer
        validations = [
            (UserDTO("", "noEmail"), "Please fill out this field."),
            (UserDTO("noAtSign", "password"), "Please include an '@' in the email address. 'noAtSign' is missing an '@'."),
            (UserDTO("nothingAfter@", "password"), "Please enter a part following '@'. 'nothingAfter@' is incomplete."),
            (UserDTO("noPassword@gmail.com", ""), "Please fill out this field.")
        ]

        for validation in validations:
            validation_check(driver, validation)

        # Test Login Alerts Appear
        alerts = [
            (UserDTO("bad@gmail.com", "password"), "Sign in failed: UserNotFoundException: User does not exist."),
            (UserDTO("admin@gmail.com", "badPassword"), "Sign in failed: NotAuthorizedException: Incorrect username or password.")
        ]

        for alert in alerts:
            alert_check(driver, alert)
    finally:
        driver.quit()

def user_login_logout(driver, user: UserDTO):
    try:
        login_step = LoginStep(driver, user, LoginMode.NORMAL)
        login_step.run()

        logout_step = LogoutStep(driver)
        logout_step.run()
    except Exception as e:
        pytest_check.fail(f"Error Occured With Login/Logout for User [{user.name}]: {e.msg}")

def validation_check(driver, validation: tuple[UserDTO, str]):
    login_step = LoginStep(driver, validation[0], LoginMode.VALIDATION)
    login_step.run()

    pytest_check.equal(validation[1], login_step.alert_validation_text)

def alert_check(driver, alert: tuple[UserDTO, str]):
    login_step = LoginStep(driver, alert[0], LoginMode.ALERT)
    login_step.run()

    pytest_check.equal(alert[1], login_step.alert_validation_text)