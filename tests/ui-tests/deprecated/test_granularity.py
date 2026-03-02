import time
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import Select
import pytest
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from test_helpers import login, select_trail_from_dropdown, getService, getOptions
from ui_config import DEFAULT_WAIT_TIME, SHORT_WAIT_TIME, MEDIUM_WAIT_TIME, DEFAULT_START_DATE, START_DATE_CLASS, GRANULARITY_ID

@pytest.mark.UI
@pytest.mark.skip(reason="deprecated")
def test_Granularity():
    """Test changing granularity setting"""
    driver = webdriver.Chrome(service=getService(), options=getOptions())

    try:
        login(driver)

        wait = WebDriverWait(driver, DEFAULT_WAIT_TIME)

        # Ensure we're in graph view (default)
        # Find and interact with granularity dropdown
        gran = wait.until(EC.presence_of_element_located((By.ID, GRANULARITY_ID)))
        gran.click()
        time.sleep(1)

        # Select a granularity option using Select class
        select = Select(gran)
        select.select_by_visible_text("Monthly")
        time.sleep(SHORT_WAIT_TIME)

        # Set start date
        start_date = wait.until(EC.presence_of_element_located((By.CLASS_NAME, START_DATE_CLASS)))
        start_date.clear()
        start_date.send_keys(DEFAULT_START_DATE + Keys.ENTER)
        time.sleep(SHORT_WAIT_TIME)
       
        # Use helper function to select trail
        select_trail_from_dropdown(driver, wait, "All Trails")
        time.sleep(MEDIUM_WAIT_TIME)
        
        # Verify granularity was set
        assert select.first_selected_option.text == "Monthly", "Granularity not set to Monthly"

    finally:
        driver.quit()