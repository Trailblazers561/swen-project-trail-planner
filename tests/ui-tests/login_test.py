import pytest
import pytest_check
from selenium_helper import SeleniumHelper as SH

from dtos.user_dto import UserDTO
from enums.user_enum import User
from steps.login.login_step import LoginStep
from steps.login.logout_step import LogoutStep

@pytest.mark.UI
def login_test():
    driver = SH.get_driver()
    users = [
        # UserDTO(user=User.ROOT_ADMIN),
        UserDTO(user=User.ADMIN),
        # UserDTO(user=User.TRAIL_MANAGER),
        # UserDTO(user=User.USER)
    ]

    for user in users:
        user_login_logout(driver, user)

    # test logging in with unregistered user
    bad_email = UserDTO(user=User.ADMIN)
    bad_email.email = "bad@gmail.com"
    login_step = LoginStep(driver, bad_email, True)
    login_step.run()

    pytest_check.equal("Sign in failed: UserNotFoundException: User does not exist.", login_step.alert_text)

    # test logging in with invalid password
    bad_password = UserDTO(user=User.ADMIN)
    bad_password.password = "HELLO!!!"
    login_step = LoginStep(driver, bad_password, True)
    login_step.run()

    pytest_check.equal("Sign in failed: NotAuthorizedException: Incorrect username or password.", login_step.alert_text)

def user_login_logout(driver, user: UserDTO):
    try:
        login_step = LoginStep(driver, user)
        login_step.run()

        logout_step = LogoutStep(driver)
        logout_step.run()
    except Exception as e:
        pytest_check.fail(f"Error Occured With Login/Logout for User [{user.name}]: {e.msg}")