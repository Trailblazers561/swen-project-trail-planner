from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium_helper import SeleniumHelper as SH

from datetime import datetime

from dtos.dashboard_filter_dto import DashboardFilterDTO
from dtos.trail_dto import TrailDTO
from dtos.trail_group_dto import TrailGroupDTO
from dtos.graph_dto import GraphDTO, LineDTO, PointDTO
from dtos.trail_status_dto import TrailStatusDTO

class EditTrailPage:
    root = (By.XPATH, "//div[@data-testid='edit-trail-group-modal']")
    # Edit
    group_select = (By.XPATH, "//select[@id='group-select']")
    # delete_trail_button = (By.XPATH, "//button[@data-testid='delete-button']") ??? supposed to be here?
    # confirm_delete_button = (By.XPATH, "//button[@data-testid='confirm-delete']")
    # cancel_delete_button = (By.XPATH, "//button[@data-testid='cancel-delete']")
    # Edit & Add
    group_name_input = (By.XPATH, "//input[@id='group-name']")
    create_update_group_button = (By.XPATH, "//button[@data-testid='confirm-button']")
    select_trail_checkbox_xpath = "//input[@data-testid='checkbox {}'}"

    def __init__(self, driver: webdriver.Chrome):
        self.driver = driver
        SH.wait_for_element_appear(self.driver, self.root)