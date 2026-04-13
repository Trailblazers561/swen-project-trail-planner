import pytest
import pytest_check
from pathlib import Path
import time

from selenium_helper import SeleniumHelper as SH
from test_data import TRAILS

from dtos.dashboard_filter_dto import DashboardFilterDTO
from dtos.trail_group_dto import TrailGroupDTO
from dtos.user_dto import UserDTO
from enums.user_enum import User
from steps.dashboard.add_trail_group_step import AddTrailGroupStep
from steps.dashboard.edit_trail_group_step import EditTrailGroupStep
from steps.dashboard.retrieve_dashboard_options_step import RetrieveDashboardOptionsStep
from steps.dashboard.retrieve_edit_trail_group_groups_step import RetrieveEditTrailGroupGroupsStep
from steps.dashboard.set_dashboard_filters_step import SetDashboardFiltersStep
from steps.login.login_step import LoginStep

@pytest.mark.UI
@pytest.mark.skip(reason="feature bugged")
def dashboard_graph_test():
    """
    Tests Everthing About The Dashboard Trail Group Options Dropdown
     - Add Trail Group
     - Edit Trail Group
     - Delete Trail Group
    """
    driver = SH.get_driver()

    try:
        # Login
        login_step = LoginStep(driver, UserDTO(user=User.ADMIN))
        login_step.run()

        # Wait for API Calls To Be Made
        SH.wait(3)

        # Create Trail Group
        group_one = TrailGroupDTO("Add Edit Group One")
        add_group_one_step = AddTrailGroupStep(driver, group_one)
        add_group_one_step.run()
        SH.wait(1)

        # Verify Present In Trail Groups Muliselect
        retrieve_added_group_one_step = RetrieveDashboardOptionsStep(driver)
        retrieve_added_group_one_step.run()

        pytest_check.is_true(group_one in retrieve_added_group_one_step.trail_groups)

        # Select Group
        select_group_one_step = SetDashboardFiltersStep(driver, DashboardFilterDTO(trail_groups={group_one}))
        select_group_one_step.run()

        # Verify Trail Mulitselect Empty
        retrieve_empty_trails_step = RetrieveDashboardOptionsStep(driver)
        retrieve_empty_trails_step.run()

        pytest_check.equal([], retrieve_empty_trails_step.trails)

        # Update Group Name And Trails
        old_name = group_one.name
        group_one.name = "Updated Group One"
        group_one.trails = {TRAILS[12]}
        update_group_one_step = EditTrailGroupStep(driver, group_one, old_name)
        update_group_one_step.run()
        SH.wait(1)

        # Verify Updated In Trail Groups Muliselect
        retrieve_updated_group_one_step = RetrieveDashboardOptionsStep(driver)
        retrieve_updated_group_one_step.run()

        pytest_check.is_true(group_one in retrieve_updated_group_one_step.trail_groups)

        # If they decide to remove the selected trail groups after updating, reselect

        # Verify Added Trail In Trails Multiselect
        retrieve_group_one_trails_step = RetrieveDashboardOptionsStep(driver)
        retrieve_group_one_trails_step.run()

        pytest_check.equal([TRAILS[12]], retrieve_group_one_trails_step.trails)

        # Delete Trail Group
        delete_group_one_step = EditTrailGroupStep(driver, group_one, delete=True)
        delete_group_one_step.run()
        SH.wait(1)

        # Verify Trail Group No Longer Present
        retrieve_deleted_group_one_step = RetrieveDashboardOptionsStep(driver)
        retrieve_deleted_group_one_step.run()

        pytest_check.is_false(group_one in retrieve_deleted_group_one_step.trail_groups)

        # Verify Trail Group Not In Edit Trail Group Dropdown
        retrieve_edit_trail_trails_step = RetrieveEditTrailGroupGroupsStep(driver)
        retrieve_edit_trail_trails_step.run()

        pytest_check.is_false(group_one in retrieve_edit_trail_trails_step.trail_groups)

        # Create Trail Group With Trails
        group_two = TrailGroupDTO("Add Edit Group Two", trails={TRAILS[12]})
        add_group_two_step = AddTrailGroupStep(driver, group_two)
        add_group_two_step.run()
        SH.wait(1)

        # Verify Trail Group Present
        retrieve_group_two_groups_step = RetrieveDashboardOptionsStep(driver)
        retrieve_group_two_groups_step.run()

        pytest_check.is_true(group_two in retrieve_group_two_groups_step.trail_groups)

        # If they decide to remove the selected trail groups after updating, reselect

        # Verify Added Trail In Trails Multiselect
        retrieve_group_two_trails_step = RetrieveDashboardOptionsStep(driver)
        retrieve_group_two_trails_step.run()

        pytest_check.equal([TRAILS[12]], retrieve_group_two_trails_step.trails)

        # Delete Trail
        delete_group_two_step = EditTrailGroupStep(driver, group_two, delete=True)
        delete_group_two_step.run()
    except:
        driver.save_screenshot(Path(__file__).parent / f"errors/add_edit_trail_group_test_error_{int(time.time())}.png")
        raise
    finally:
        driver.quit()