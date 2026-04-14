import pytest
import pytest_check
from pathlib import Path
import time

from datetime import datetime

from selenium_helper import SeleniumHelper as SH
from test_data import TRAILS, TRAIL_GROUPS, retrieve_graph

from dtos.dashboard_filter_dto import DashboardFilterDTO
from dtos.trail_dto import TrailDTO
from dtos.user_dto import UserDTO
from enums.granularity import Granularity
from enums.user_enum import User
from steps.dashboard.retrieve_dashboard_options_step import RetrieveDashboardOptionsStep
from steps.dashboard.retrieve_graph_step import RetrieveGraphStep
from steps.dashboard.set_dashboard_filters_step import SetDashboardFiltersStep
from steps.login.login_step import LoginStep

@pytest.mark.UI
def dashboard_graph_test():
    """
    Tests Everthing About The Dashboard Graph
     - Date Rage
     - Granularity
     - Trails Multiselct
     - Trail Group Multiselect
     - Graph
    """
    driver = SH.get_driver()

    try:
        # Login
        login_step = LoginStep(driver, UserDTO(user=User.ADMIN))
        login_step.run()

        # Wait for API Calls To Be Made
        SH.wait(3)

        # Verify All Trails and Trail Groups Present
        retrieve_all_trails_step = RetrieveDashboardOptionsStep(driver)
        retrieve_all_trails_step.run()

        pytest_check.equal(set(TRAILS.values()), set(retrieve_all_trails_step.trails))
        pytest_check.equal({group.name for group in TRAIL_GROUPS}, set(group.name for group in retrieve_all_trails_step.trail_groups))

        # Verify Correct Granularity Options Appear With Date Ranges
        granularities = [
            # Verify 1825+ Day Range Granularities: Year, Month
            (DashboardFilterDTO(datetime.fromisoformat("2020-01-01"), datetime.fromisoformat("2026-01-01")), [Granularity.YEAR, Granularity.MONTH]),
            # Verify 730-1824 Day Range Granularities: Year, Month, Week
            (DashboardFilterDTO(datetime.fromisoformat("2024-01-01"), datetime.fromisoformat("2026-01-01")), [Granularity.YEAR, Granularity.MONTH, Granularity.WEEK]),
            # Verify 180-729 Day Range Granularities: Month, Week
            (DashboardFilterDTO(datetime.fromisoformat("2025-01-01"), datetime.fromisoformat("2026-01-01")), [Granularity.MONTH, Granularity.WEEK]),
            # Verify 60-179 Day Range Granularities: Month, Week, Day
            (DashboardFilterDTO(datetime.fromisoformat("2026-01-01"), datetime.fromisoformat("2026-03-31")), [Granularity.MONTH, Granularity.WEEK, Granularity.DAY]),
            # Verify 30-59 Day Range Granularities: Week, Day
            (DashboardFilterDTO(datetime.fromisoformat("2026-01-01"), datetime.fromisoformat("2026-02-01")), [Granularity.WEEK, Granularity.DAY]),
            # Verify 4-29 Day Range Granularities: Day
            (DashboardFilterDTO(datetime.fromisoformat("2026-01-01"), datetime.fromisoformat("2026-01-15")), [Granularity.DAY]),
            # Verify 0-3 Day Range Granularities: Day, Hour
            (DashboardFilterDTO(datetime.fromisoformat("2026-01-01"), datetime.fromisoformat("2026-01-03")), [Granularity.DAY, Granularity.HOUR]),
        ]
        for granularity in granularities:
            verify_granularity(driver, granularity)

        # Verify Empty Graph
        retrieve_empty_graph_step = RetrieveGraphStep(driver)
        retrieve_empty_graph_step.run()

        empty_graph = retrieve_graph(datetime(2026, 1, 1), datetime(2026, 1, 2), Granularity.DAY, [])
        pytest_check.equal(empty_graph, retrieve_empty_graph_step.graph)

        # Select First Two Trail Groups and Verify Trails Appear
        group_filter = DashboardFilterDTO(trail_groups={TRAIL_GROUPS[0], TRAIL_GROUPS[1]})
        set_group_filter_step = SetDashboardFiltersStep(driver, group_filter)
        set_group_filter_step.run()

        retrieve_group_trails_step = RetrieveDashboardOptionsStep(driver)
        retrieve_group_trails_step.run()
        pytest_check.equal({trail.name for trail in TRAIL_GROUPS[0].trails.union(TRAIL_GROUPS[1].trails)}, {trail.name for trail in retrieve_group_trails_step.trails})

        # Test Graph Data For Each Granularity
        selected_trails = {next(iter(TRAIL_GROUPS[0].trails)), next(iter(TRAIL_GROUPS[1].trails))}
        granularity_filters = [
            DashboardFilterDTO(datetime.fromisoformat("2024-01-01"), datetime.fromisoformat("2026-01-01"), Granularity.YEAR, trails=selected_trails),
            DashboardFilterDTO(datetime.fromisoformat("2026-01-15"), datetime.fromisoformat("2026-03-16"), Granularity.MONTH, trails=selected_trails),
            DashboardFilterDTO(datetime.fromisoformat("2026-01-15"), datetime.fromisoformat("2026-03-16"), Granularity.WEEK, trails=selected_trails),
            DashboardFilterDTO(datetime.fromisoformat("2026-01-15"), datetime.fromisoformat("2026-03-16"), Granularity.DAY, trails=selected_trails),
            DashboardFilterDTO(datetime.fromisoformat("2026-01-01"), datetime.fromisoformat("2026-01-03"), Granularity.HOUR, trails=selected_trails),
        ]
        for granularity_filter in granularity_filters:
            verify_granularity_filter(driver, granularity_filter, selected_trails)
        pytest_check.fail("Uncomment API Tests and Destroy")
    except:
        driver.save_screenshot(Path(__file__).parent / f"errors/dashboard_graph_test_error_{int(time.time())}.png")
        raise
    finally:
        driver.quit()

def verify_granularity(driver, granularity: list[DashboardFilterDTO, list[Granularity]]):
    filter = granularity[0]

    set_dashboard_filter_step = SetDashboardFiltersStep(driver, filter)
    set_dashboard_filter_step.run()

    retrieve_granularities_step = RetrieveDashboardOptionsStep(driver)
    retrieve_granularities_step.run()
    pytest_check.equal(granularity[1], retrieve_granularities_step.granularities)

def verify_granularity_filter(driver, granularity_filter: DashboardFilterDTO, selected_trails: set[TrailDTO]):
    set_dashboard_filter_step = SetDashboardFiltersStep(driver, granularity_filter)
    set_dashboard_filter_step.run()
    SH.wait(10)

    retrieve_graph_step = RetrieveGraphStep(driver)
    retrieve_graph_step.run()

    expected_graph = retrieve_graph(granularity_filter.date_start, granularity_filter.date_end, granularity_filter.granularity, [trail.id for trail in selected_trails])
    expected_graph.compare(retrieve_graph_step.graph)