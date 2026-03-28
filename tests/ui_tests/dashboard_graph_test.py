import pytest
import pytest_check
from selenium_helper import SeleniumHelper as SH

from datetime import datetime

from dtos.user_dto import UserDTO
from enums.user_enum import User
from steps.login.login_step import LoginStep
from dtos.dashboard_filter_dto import DashboardFilterDTO
from dtos.trail_dto import TrailDTO
from dtos.trail_group_dto import TrailGroupDTO


from selenium.webdriver.common.by import By
from selenium_helper import SeleniumHelper as SH
@pytest.mark.UI
def dashboard_graph_test():
    driver = SH.get_driver()
    dashboard_filter = DashboardFilterDTO(datetime.strptime("07/01/2025", "%m/%d/%Y"), datetime.strptime("07/31/2025", "%m/%d/%Y"), {TrailDTO("RT Test Trail 1")}, {TrailGroupDTO("RT Test Trail Group 1")})

    try:
        login_step = LoginStep(driver, UserDTO(user=User.ADMIN))
        login_step.run()

        #
        from pages.dashboard_page import DashboardPage
        from steps.dashboard.export_data_step import ExportDataStep
        step = ExportDataStep(driver)
        step.run()
        path = step.export_file_path
        # po = DashboardPage(driver)
        # po.set_dashboard_filters(dashboard_filter)
        # filters = po.retrieve_dashboard_filters()
        # po.click_associate_device()
        # po.click_export_data()
        # po.click_import_data()
        # po.click_toggle_view()
        # po.click_add_trail()
        # po.click_edit_trail()
        # po.click_add_trail_group()
        # po.click_edit_trail_group()
        # graph = po.retrieve_graph()
        statusus = po.retrieve_trail_status()
        print()
        
    except Exception as e:
        print(e)
    finally:
        driver.quit()
dashboard_graph_test()