import pytest
import pytest_check
from pathlib import Path
import time

from selenium_helper import SeleniumHelper as SH
from test_data import retrieve_trail_status_overview

from dtos.trail_status_dto import TrailStatusDTO
from dtos.user_dto import UserDTO
from enums.trail_status_column import TrailStatusColumn
from enums.user_enum import User
from steps.dashboard.click_trail_status_header_step import ClickTrailStatusHeaderStep
from steps.dashboard.retrieve_trail_status_step import RetrieveTrailStatusesStep
from steps.dashboard.toggle_dashboard_view_step import ToggleDashboardViewStep
from steps.login.login_step import LoginStep

@pytest.mark.UI
def dashboard_trail_status_test():
    """
    Tests Everthing About The Dashboard Trail Status Overview
     - Table Data
     - Table Sorting
    """
    driver = SH.get_driver()

    try:
        pass
        # Login
        login_step = LoginStep(driver, UserDTO(user=User.ADMIN))
        login_step.run()

        # Toggle View To Trail Status Overview
        toggle_dashboard_view_step = ToggleDashboardViewStep(driver)
        toggle_dashboard_view_step.run()
        SH.wait(3)

        # Retrieve Default Trail Status Overview and Verify
        retrieve_default_statuses_step = RetrieveTrailStatusesStep(driver)
        retrieve_default_statuses_step.run()

        compare_trail_status_lists(retrieve_trail_status_overview(), retrieve_default_statuses_step.trail_statuses, "Default Trail Status Overview")

        # Click Trail Name Header and Verify
        sorted_columns = [
            (TrailStatusColumn.TRAIL_NAME, False, "Ascending Trail Name"),
            (TrailStatusColumn.WEEKLY_COUNT, False, "Ascending Weekly Count"),
            (TrailStatusColumn.BATTERY_STATUS, False, "Ascending Battery Status"),
            (TrailStatusColumn.LAST_UPDATED, False, "Ascending Last Updated"),
            (TrailStatusColumn.LAST_UPDATED, True, "Descending Last Updated"),
            (TrailStatusColumn.BATTERY_STATUS, True, "Descending Battery Status"),
            (TrailStatusColumn.WEEKLY_COUNT, True, "Descending Weekly Count"),
            (TrailStatusColumn.TRAIL_NAME, True, "Descending Trail Name"),
        ]
        for sorted_column in sorted_columns:
            verify_trail_header(driver, *sorted_column)
    except:
        # Save Screenshot of When Error Occured
        driver.save_screenshot(Path(__file__).parent / f"errors/dashboard_trail_status_test_error_{int(time.time())}.png")
        raise
    finally:
        driver.quit()

def verify_trail_header(driver, column: TrailStatusColumn, reverse: bool, label: str):
    driver.save_screenshot(Path(__file__).parent / f"errors/dashboard_trail_status_test_before_sort_{label.lower().replace(' ', '_')}_{int(time.time())}.png")
    # Click Trail Status Header to Sort Column
    click_trail_status_header_step = ClickTrailStatusHeaderStep(driver, column)
    click_trail_status_header_step.run()
    driver.save_screenshot(Path(__file__).parent / f"errors/dashboard_trail_status_test_after_sort_{label.lower().replace(' ', '_')}_{int(time.time())}.png")

    # Retrieve Column
    retrieve_trail_statuses_step = RetrieveTrailStatusesStep(driver)
    retrieve_trail_statuses_step.run()

    # Verify Properly Sorted
    # if retrieve_trail_status_overview(column, reverse) != retrieve_trail_statuses_step.trail_statuses:
    #     driver.save_screenshot(Path(__file__).parent / f"errors/dashboard_trail_status_test_mismatch_{label.lower().replace(' ', '_')}_{int(time.time())}.png")
    compare_trail_status_lists(retrieve_trail_status_overview(column, reverse), retrieve_trail_statuses_step.trail_statuses, label)

def compare_trail_status_lists(expected: list[TrailStatusDTO], actual: list[TrailStatusDTO], label: str):
    if len(expected) != len(actual):
        pytest_check.equal(len(expected), len(actual), f"Length of {label} Expected and Actaul Different")
    else:
        for e, a in zip(expected, actual):
            e.compare(a, label)