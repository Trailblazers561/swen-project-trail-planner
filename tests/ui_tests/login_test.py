import pytest
import pytest_check
from pathlib import Path
import time

from selenium_helper import SeleniumHelper as SH

from dtos.user_dto import UserDTO
from enums.login_mode import LoginMode
from enums.user_action import UserAction
from enums.user_enum import User
from enums.user_role import UserRole
from steps.login.login_step import LoginStep
from steps.other.perform_user_action_step import PerformUserActionStep
from steps.other.retrieve_navbar_information_step import RetrieveNavbarInformationStep

@pytest.mark.UI
def login_test():
    """
    Tests Everthing About Logging In
     - Login With Each User
     - Login Error Messages
    """
    driver = SH.get_driver()

    try:
        # Retrieve Initial Navbar Information and Verify
        retrieve_guest_information_step = RetrieveNavbarInformationStep(driver)
        retrieve_guest_information_step.run()

        pytest_check.equal("", retrieve_guest_information_step.username)
        pytest_check.equal(UserRole.GUEST, retrieve_guest_information_step.user_role)

        # Go To Login For First User
        click_login_step = PerformUserActionStep(driver, UserAction.LOGIN_LOGOUT)
        click_login_step.run()

        # Test Logging In With Correct Users
        users = [
            UserDTO(user=User.ROOT_ADMIN),
            UserDTO(user=User.ADMIN),
            UserDTO(user=User.TRAIL_MANAGER),
            UserDTO(user=User.USER)
        ]

        for user in users:
            user_login_logout(driver, user)

        # Test Validation Popups Appaer
        validations = [
            (UserDTO("", "noEmail"), "Please fill out this field."),
            (UserDTO("noPassword", ""), "Please fill out this field.")
        ]

        for validation in validations:
            validation_check(driver, validation)

        # Test Login Alerts Appear
        alerts = [
            (UserDTO("bad", "password"), "No account was found with the specified username or email"),
            (UserDTO("admin", "badPassword"), "Incorrect username/email or password")
        ]

        for alert in alerts:
            alert_check(driver, alert)
    except:
        # Save Screenshot of When Error Occured
        driver.save_screenshot(Path(__file__).parent / f"errors/login_test_error_{int(time.time())}.png")
        raise
    finally:
        driver.quit()

def user_login_logout(driver, user: UserDTO):
    try:
        # Login as User With Username
        login_username_step = LoginStep(driver, user, LoginMode.NORMAL)
        login_username_step.run()

        # Validate Navbar Displays Appropriate Role
        retrieve_navbar_username_information_step = RetrieveNavbarInformationStep(driver)
        retrieve_navbar_username_information_step.run()

        pytest_check.equal(user.name, retrieve_navbar_username_information_step.username)
        pytest_check.equal(user.role, retrieve_navbar_username_information_step.user_role)

        # Logout For Email Login
        logout_username_step = PerformUserActionStep(driver, UserAction.LOGIN_LOGOUT)
        logout_username_step.run()

        # Login as User With Email
        login_email_step = LoginStep(driver, user, LoginMode.NORMAL, False)
        login_email_step.run()

        # Validate Navbar Displays Appropriate Role
        retrieve_navbar_email_information_step = RetrieveNavbarInformationStep(driver)
        retrieve_navbar_email_information_step.run()

        pytest_check.equal(user.name, retrieve_navbar_email_information_step.username)
        pytest_check.equal(user.role, retrieve_navbar_email_information_step.user_role)

        # Logout For Next User
        logout_email_step = PerformUserActionStep(driver, UserAction.LOGIN_LOGOUT)
        logout_email_step.run()
    except Exception as e:
        pytest_check.fail(f"Error Occured With Login/Logout for User [{user.name}]: {e.msg}")

def validation_check(driver, validation: tuple[UserDTO, str]):
    # Login (Should Cause a Validation Popup)
    login_step = LoginStep(driver, validation[0], LoginMode.VALIDATION)
    login_step.run()

    pytest_check.equal(validation[1], login_step.alert_validation_text)

def alert_check(driver, alert: tuple[UserDTO, str]):
    # Login (Should Cause an Alert)
    login_step = LoginStep(driver, alert[0], LoginMode.ALERT)
    login_step.run()

    pytest_check.equal(alert[1], login_step.alert_validation_text)