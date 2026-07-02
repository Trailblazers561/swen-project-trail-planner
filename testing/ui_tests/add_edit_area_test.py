import pytest
import pytest_check
from pathlib import Path
import time

from selenium_helper import SeleniumHelper as SH
from test_data import TRAILS

from dtos.dashboard_filter_dto import DashboardFilterDTO
from dtos.area_dto import AreaDTO
from dtos.user_dto import UserDTO
from enums.user_action import UserAction
from enums.user_enum import User
from steps.dashboard.add_area_step import AddAreaStep
from steps.dashboard.edit_area_step import EditAreaStep
from steps.dashboard.retrieve_dashboard_options_step import RetrieveDashboardOptionsStep
from steps.dashboard.retrieve_edit_area_areas_step import RetrieveEditAreaAreasStep
from steps.dashboard.set_dashboard_filters_step import SetDashboardFiltersStep
from steps.login.login_step import LoginStep
from steps.other.perform_user_action_step import PerformUserActionStep

@pytest.mark.UI
@pytest.mark.skip(reason="feature bugged")
def add_edit_area_test():
    """
    Tests Everthing About The Dashboard Area Options Dropdown
     - Add Area
     - Edit Area
     - Delete Area
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

        # Create Area
        area_one = AreaDTO("Add Edit Area One")
        add_area_one_step = AddAreaStep(driver, area_one)
        add_area_one_step.run()
        SH.wait(1)

        # Verify Present In Areas Muliselect
        retrieve_added_area_one_step = RetrieveDashboardOptionsStep(driver)
        retrieve_added_area_one_step.run()

        pytest_check.is_true(area_one in retrieve_added_area_one_step.areas)

        # Select Area
        select_area_one_step = SetDashboardFiltersStep(driver, DashboardFilterDTO(areas={area_one}))
        select_area_one_step.run()

        # Verify Trail Mulitselect Empty
        retrieve_empty_trails_step = RetrieveDashboardOptionsStep(driver)
        retrieve_empty_trails_step.run()

        pytest_check.equal([], retrieve_empty_trails_step.trails)

        # Update Area Name And Trails
        old_name = area_one.name
        area_one.name = "Updated Area One"
        area_one.trails = {TRAILS[12]}
        update_area_one_step = EditAreaStep(driver, area_one, old_name)
        update_area_one_step.run()
        SH.wait(1)

        # Verify Updated In Areas Muliselect
        retrieve_updated_area_one_step = RetrieveDashboardOptionsStep(driver)
        retrieve_updated_area_one_step.run()

        pytest_check.is_true(area_one in retrieve_updated_area_one_step.areas)

        # If they decide to remove the selected areas after updating, reselect

        # Verify Added Trail In Trails Multiselect
        retrieve_area_one_trails_step = RetrieveDashboardOptionsStep(driver)
        retrieve_area_one_trails_step.run()

        pytest_check.equal([TRAILS[12]], retrieve_area_one_trails_step.trails)

        # Delete Area
        delete_area_one_step = EditAreaStep(driver, area_one, delete=True)
        delete_area_one_step.run()
        SH.wait(1)

        # Verify Area No Longer Present
        retrieve_deleted_area_one_step = RetrieveDashboardOptionsStep(driver)
        retrieve_deleted_area_one_step.run()

        pytest_check.is_false(area_one in retrieve_deleted_area_one_step.areas)

        # Verify Area Not In Edit Area Dropdown
        retrieve_edit_trail_trails_step = RetrieveEditAreaAreasStep(driver)
        retrieve_edit_trail_trails_step.run()

        pytest_check.is_false(area_one in retrieve_edit_trail_trails_step.areas)

        # Create Area With Trails
        area_two = AreaDTO("Add Edit Area Two", trails={TRAILS[12]})
        add_area_two_step = AddAreaStep(driver, area_two)
        add_area_two_step.run()
        SH.wait(1)

        # Verify Area Present
        retrieve_area_two_areas_step = RetrieveDashboardOptionsStep(driver)
        retrieve_area_two_areas_step.run()

        pytest_check.is_true(area_two in retrieve_area_two_areas_step.areas)

        # If they decide to remove the selected areas after updating, reselect

        # Verify Added Trail In Trails Multiselect
        retrieve_area_two_trails_step = RetrieveDashboardOptionsStep(driver)
        retrieve_area_two_trails_step.run()

        pytest_check.equal([TRAILS[12]], retrieve_area_two_trails_step.trails)

        # Delete Trail
        delete_area_two_step = EditAreaStep(driver, area_two, delete=True)
        delete_area_two_step.run()
    except:
        # Save Screenshot of When Error Occured
        driver.save_screenshot(Path(__file__).parent / f"errors/add_edit_area_test_error_{int(time.time())}.png")
        raise
    finally:
        driver.quit()