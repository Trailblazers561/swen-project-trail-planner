import pytest
import pytest_check
from pathlib import Path
import time

from datetime import datetime
import csv

from selenium_helper import SeleniumHelper as SH
from test_data import TRAIL_GROUPS, retrieve_csv_list

from dtos.dashboard_filter_dto import DashboardFilterDTO
from dtos.user_dto import UserDTO
from enums.granularity import Granularity
from enums.user_enum import User
from steps.dashboard.export_data_step import ExportDataStep
from steps.dashboard.set_dashboard_filters_step import SetDashboardFiltersStep
from steps.login.login_step import LoginStep

@pytest.mark.UI
def import_export_data_test():
    """
    Tests Everthing About Import/Export
     - Exports Each Granularity
     - Import
    """
    driver = SH.get_driver()

    try:
        # Login
        login_step = LoginStep(driver, UserDTO(user=User.ADMIN))
        login_step.run()

        # Wait for API Calls To Be Made
        SH.wait(3)

        # Verify Export For Each Granularity
        selected_trails = {next(iter(TRAIL_GROUPS[0].trails)), next(iter(TRAIL_GROUPS[1].trails))}
        granularity_filters = [
            DashboardFilterDTO(datetime.fromisoformat("2024-01-01"), datetime.fromisoformat("2026-01-01"), Granularity.YEAR, trails=selected_trails),
            DashboardFilterDTO(datetime.fromisoformat("2026-01-15"), datetime.fromisoformat("2026-03-16"), Granularity.MONTH, trails=selected_trails),
            DashboardFilterDTO(datetime.fromisoformat("2026-01-15"), datetime.fromisoformat("2026-03-16"), Granularity.WEEK, trails=selected_trails),
            DashboardFilterDTO(datetime.fromisoformat("2026-01-15"), datetime.fromisoformat("2026-03-16"), Granularity.DAY, trails=selected_trails),
            DashboardFilterDTO(datetime.fromisoformat("2026-01-01"), datetime.fromisoformat("2026-01-03T23:00:00-05:00"), Granularity.HOUR, trails=selected_trails),
        ]
        for filter in granularity_filters:
            verify_export(driver, filter)

        # TODO: Import

    except:
        # Save Screenshot of When Error Occured
        driver.save_screenshot(Path(__file__).parent / f"errors/import_export_data_test_error_{int(time.time())}.png")
        raise
    finally:
        driver.quit()

def verify_export(driver, filter: DashboardFilterDTO):
    # Set Export Filters 
    set_dashboard_filter_step = SetDashboardFiltersStep(driver, filter)
    set_dashboard_filter_step.run()

    # Export Data
    export_data_step = ExportDataStep(driver)
    export_data_step.run()

    pytest_check.is_not_none(export_data_step.export_file_path, f"Export File Not Found For Granularity [{filter.granularity}]")
    if not export_data_step.export_file_path: return

    # Verify File Matches
    with open(export_data_step.export_file_path) as f:
        reader = csv.DictReader(f)
        expected_headers = ["Trail ID", "Trail Name", "Start Time", f"{filter.granularity.value} Count", "Battery %"]
        pytest_check.assert_equal(expected_headers, reader.fieldnames)
        if expected_headers != reader.fieldnames: return
        expected_rows = retrieve_csv_list(filter.date_start, filter.date_end, filter.granularity, [trail.id for trail in filter.trails])
        for i, row in enumerate(reader):
            if (i >= len(expected_rows)):
                pytest_check.fail(f"Export CSV Contained Too Many Rows For Granularity [{filter.granularity.value}]")
                break
            pytest_check.equal(expected_rows[i], row)
        pytest_check.equal(len(expected_rows), i + 1, f"Export CSV Didn't Contain All Rows For Granularity [{filter.granularity.value}]")