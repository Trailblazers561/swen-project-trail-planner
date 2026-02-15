import time
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
import pytest
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from test_helpers import login, select_trail_from_dropdown, getService, getOptions
from ui_config import DEFAULT_WAIT_TIME, SHORT_WAIT_TIME, DEFAULT_START_DATE, TEST_START_DATE, TEST_END_DATE, START_DATE_CLASS, END_DATE_CLASS

@pytest.mark.UI
def test_EditDates():
    """Test editing start and end dates"""
    driver = webdriver.Chrome(service=getService(), options=getOptions())

    try:
        login(driver)

        wait = WebDriverWait(driver, DEFAULT_WAIT_TIME)

        # Ensure we're in graph view
        # Set initial start date
        start_date = wait.until(EC.presence_of_element_located((By.CLASS_NAME, START_DATE_CLASS)))
        start_date.clear()
        start_date.send_keys(DEFAULT_START_DATE + Keys.ENTER)
        time.sleep(SHORT_WAIT_TIME)
       
        # Use helper function to select trail
        select_trail_from_dropdown(driver, wait, "All Trails")
        time.sleep(SHORT_WAIT_TIME)

        # Edit start date
        start_date.clear()
        start_date.send_keys(TEST_START_DATE + Keys.ENTER)
        time.sleep(SHORT_WAIT_TIME)

        # Edit end date
        end_date = wait.until(EC.presence_of_element_located((By.CLASS_NAME, END_DATE_CLASS)))
        end_date.clear()
        end_date.send_keys(TEST_END_DATE + Keys.ENTER)
        time.sleep(SHORT_WAIT_TIME)
        
        # Verify dates were updated
        assert start_date.get_attribute("value") is not None, "Start date not set"
        assert end_date.get_attribute("value") is not None, "End date not set"

    finally:
        driver.quit()