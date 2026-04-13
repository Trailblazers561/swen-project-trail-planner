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
from steps.dashboard.retrieve_trail_status_step import RetrieveTrailStatusStep
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
        retrieve_default_status_step = RetrieveTrailStatusStep(driver)
        retrieve_default_status_step.run()

        compare_trail_status_lists(retrieve_trail_status_overview(), retrieve_default_status_step.trail_status, "Default Trail Status Overview")

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
        driver.save_screenshot(Path(__file__).parent / f"errors/dashboard_trail_status_test_error_{int(time.time())}.png")
        raise
    finally:
        driver.quit()

def verify_trail_header(driver, column: TrailStatusColumn, reverse: bool, label: str):
    try:
        # SH.wait(3)
        # Click Trail Status Header to Sort Column
        click_trail_status_header_step = ClickTrailStatusHeaderStep(driver, column)
        click_trail_status_header_step.run()

        # Retrieve Column
        retrieve_default_status_step = RetrieveTrailStatusStep(driver)
        retrieve_default_status_step.run()

        # Verify Properly Sorted
        compare_trail_status_lists(retrieve_trail_status_overview(column, reverse), retrieve_default_status_step.trail_status, label)
    except:
        raise

def compare_trail_status_lists(expected: list[TrailStatusDTO], actual: list[TrailStatusDTO], label: str):
    if len(expected) != len(actual):
        pytest_check.equal(len(expected), len(actual), f"Length of {label} Expected and Actaul Different")
    else:
        for e, a in zip(expected, actual):
            e.compare(a, label)