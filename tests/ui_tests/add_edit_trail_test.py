import pytest
import pytest_check
from pathlib import Path
import time

from selenium_helper import SeleniumHelper as SH
from test_data import TRAIL_GROUPS

from dtos.dashboard_filter_dto import DashboardFilterDTO
from dtos.trail_dto import TrailDTO
from dtos.user_dto import UserDTO
from enums.user_enum import User
from steps.dashboard.add_trail_step import AddTrailStep
from steps.dashboard.edit_trail_step import EditTrailStep
from steps.dashboard.retrieve_dashboard_options_step import RetrieveDashboardOptionsStep
from steps.dashboard.retrieve_edit_trail_trails_step import RetrieveEditTrailTrailsStep
from steps.dashboard.set_dashboard_filters_step import SetDashboardFiltersStep
from steps.login.login_step import LoginStep

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
        # Login
        login_step = LoginStep(driver, UserDTO(user=User.ADMIN))
        login_step.run()

        # Wait for API Calls To Be Made
        SH.wait(3)

        # Create Trail
        trail_one = TrailDTO("Add Edit Trail One")
        add_trail_one_step = AddTrailStep(driver, trail_one)
        add_trail_one_step.run()
        SH.wait(1)

        # Verify Present In Trails Muliselect
        retrieve_added_trail_one_step = RetrieveDashboardOptionsStep(driver)
        retrieve_added_trail_one_step.run()

        pytest_check.is_true(trail_one in retrieve_added_trail_one_step.trails)

        # Update Trail Name And Group
        old_name = trail_one.name
        trail_one.name = "Updated Trail One"
        trail_one.trail_group_name = TRAIL_GROUPS[3].name
        update_trail_one_step = EditTrailStep(driver, trail_one, old_name)
        update_trail_one_step.run()
        SH.wait(1)

        # Verify Updated In Trails Muliselect
        retrieve_updated_trail_one_step = RetrieveDashboardOptionsStep(driver)
        retrieve_updated_trail_one_step.run()

        pytest_check.is_true(trail_one in retrieve_updated_trail_one_step.trails)

        # Select Group
        select_trail_one_group_step = SetDashboardFiltersStep(driver, DashboardFilterDTO(trail_groups={TRAIL_GROUPS[3]}))
        select_trail_one_group_step.run()

        # Verify Trail Still Present
        retrieve_grouped_trail_one_step = RetrieveDashboardOptionsStep(driver)
        retrieve_grouped_trail_one_step.run()

        pytest_check.is_true(trail_one in retrieve_grouped_trail_one_step.trails)

        # Delete Trail
        delete_trail_one_step = EditTrailStep(driver, trail_one, delete=True)
        delete_trail_one_step.run()
        SH.wait(1)

        # Verify Trail No Longer Present
        retrieve_deleted_trail_one_step = RetrieveDashboardOptionsStep(driver)
        retrieve_deleted_trail_one_step.run()

        pytest_check.is_false(trail_one in retrieve_deleted_trail_one_step.trails)

        # Verify Trail Not In Edit Trail Dropdown
        retrieve_edit_trail_trails_step = RetrieveEditTrailTrailsStep(driver)
        retrieve_edit_trail_trails_step.run()

        pytest_check.is_false(trail_one in retrieve_edit_trail_trails_step.trails)

        # Create Trail With Group
        trail_two = TrailDTO("Add Edit Trail Two", trail_group_name=TRAIL_GROUPS[3].name)
        add_trail_two_step = AddTrailStep(driver, trail_two)
        add_trail_two_step.run()
        SH.wait(1)

        # Verify Trail Present (Group Still Selected)
        retrieve_grouped_trail_two_step = RetrieveDashboardOptionsStep(driver)
        retrieve_grouped_trail_two_step.run()

        pytest_check.is_true(trail_two in retrieve_grouped_trail_two_step.trails)

        # Delete Trail
        delete_trail_two_step = EditTrailStep(driver, trail_two, delete=True)
        delete_trail_two_step.run()
        SH.wait(1)
    except:
        driver.save_screenshot(Path(__file__).parent / f"errors/add_edit_trail_test_error_{int(time.time())}.png")
        raise
    finally:
        driver.quit()