import pytest
import pytest_check
from pathlib import Path
import time

from selenium_helper import SeleniumHelper as SH
from test_data import AREAS

from dtos.dashboard_filter_dto import DashboardFilterDTO
from dtos.trail_dto import TrailDTO
from dtos.user_dto import UserDTO
from enums.user_action import UserAction
from enums.user_enum import User
from steps.dashboard.add_trail_step import AddTrailStep
from steps.dashboard.edit_trail_step import EditTrailStep
from steps.dashboard.retrieve_dashboard_options_step import RetrieveDashboardOptionsStep
from steps.dashboard.retrieve_edit_trail_trails_step import RetrieveEditTrailTrailsStep
from steps.dashboard.set_dashboard_filters_step import SetDashboardFiltersStep
from steps.login.login_step import LoginStep
from steps.other.perform_user_action_step import PerformUserActionStep

@pytest.mark.UI
def add_edit_trail_test():
    """
    Tests Everthing About The Dashboard Trail Options Dropdown
     - Add Trail
     - Edit Trail
     - Delete Trail
    """
    driver = SH.get_driver()

    try:
        # Go to Dashboard (Replace When Official Dashboard Button Becomes A Thing)
        driver.get(driver.current_url.replace("home", "dashboard"))

        # Go To Login
        click_login_step = PerformUserActionStep(driver, UserAction.LOGIN_LOGOUT)
        click_login_step.run()

        # Login
        login_step = LoginStep(driver, UserDTO(user=User.TRAIL_MANAGER))
        login_step.run()

        # Wait for API Calls To Be Made
        SH.wait(3)

        # Create Trail
        trail_one = TrailDTO("Add Edit Trail One")
        add_trail_one_step = AddTrailStep(driver, trail_one)
        add_trail_one_step.run()

        # Verify Present In Trails Muliselect
        retrieve_added_trail_one_step = RetrieveDashboardOptionsStep(driver)
        retrieve_added_trail_one_step.run()

        pytest_check.is_true(trail_one in retrieve_added_trail_one_step.trails)

        # Update Trail Name And Area
        old_name = trail_one.name
        trail_one.name = "Updated Trail One"
        trail_one.area_name = AREAS[3].name
        update_trail_one_step = EditTrailStep(driver, trail_one, old_name)
        update_trail_one_step.run()

        # Verify Updated In Trails Muliselect
        retrieve_updated_trail_one_step = RetrieveDashboardOptionsStep(driver)
        retrieve_updated_trail_one_step.run()

        pytest_check.is_true(trail_one in retrieve_updated_trail_one_step.trails)

        # If We Don't Find New Trail One Try Deleting The Old Name And End Early
        if trail_one not in retrieve_updated_trail_one_step.trails:
            trail_one.name = old_name
            delete_old_trail_one_step = EditTrailStep(driver, trail_one, delete=True)
            delete_old_trail_one_step.run()
            return

        # Select Area
        select_trail_one_area_step = SetDashboardFiltersStep(driver, DashboardFilterDTO(areas={AREAS[3]}))
        select_trail_one_area_step.run()

        # Verify Trail Still Present
        retrieve_areaed_trail_one_step = RetrieveDashboardOptionsStep(driver)
        retrieve_areaed_trail_one_step.run()

        pytest_check.is_true(trail_one in retrieve_areaed_trail_one_step.trails)

        # Delete Trail
        delete_trail_one_step = EditTrailStep(driver, trail_one, delete=True)
        delete_trail_one_step.run()

        # Verify Trail No Longer Present
        retrieve_deleted_trail_one_step = RetrieveDashboardOptionsStep(driver)
        retrieve_deleted_trail_one_step.run()

        pytest_check.is_false(trail_one in retrieve_deleted_trail_one_step.trails)

        # Verify Trail Not In Edit Trail Dropdown
        retrieve_edit_trail_trails_step = RetrieveEditTrailTrailsStep(driver)
        retrieve_edit_trail_trails_step.run()

        pytest_check.is_false(trail_one in retrieve_edit_trail_trails_step.trails)

        # Create Trail With Area
        trail_two = TrailDTO("Add Edit Trail Two", area_name=AREAS[3].name)
        add_trail_two_step = AddTrailStep(driver, trail_two)
        add_trail_two_step.run()

        # Verify Trail Present (Area Still Selected)
        retrieve_areaed_trail_two_step = RetrieveDashboardOptionsStep(driver)
        retrieve_areaed_trail_two_step.run()

        pytest_check.is_true(trail_two in retrieve_areaed_trail_two_step.trails)

        # Delete Trail
        delete_trail_two_step = EditTrailStep(driver, trail_two, delete=True)
        delete_trail_two_step.run()

        # Verify Trail No Longer Present
        retrieve_deleted_trail_two_step = RetrieveDashboardOptionsStep(driver)
        retrieve_deleted_trail_two_step.run()

        pytest_check.is_false(trail_two in retrieve_deleted_trail_two_step.trails)
    except:
        # Save Screenshot of When Error Occured
        driver.save_screenshot(Path(__file__).parent / f"errors/add_edit_trail_test_error_{int(time.time())}.png")
        raise
    finally:
        driver.quit()