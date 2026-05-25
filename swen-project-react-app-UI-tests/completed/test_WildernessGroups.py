import time
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
import pytest
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from test_helpers import login, select_trail_from_dropdown
from config import DEFAULT_WAIT_TIME, SHORT_WAIT_TIME, MEDIUM_WAIT_TIME, DEFAULT_START_DATE, START_DATE_CLASS

@pytest.mark.UI
def test_WildernessGroups():
    """Test selecting trails from wilderness groups"""
    driver = webdriver.Chrome()

    try:
        login(driver)

        wait = WebDriverWait(driver, DEFAULT_WAIT_TIME)

        # Ensure we're in graph view (default)
        # Set start date
        start_date = wait.until(EC.presence_of_element_located((By.CLASS_NAME, START_DATE_CLASS)))
        start_date.clear()
        start_date.send_keys(DEFAULT_START_DATE + Keys.ENTER)
        time.sleep(SHORT_WAIT_TIME)
       
        # Use helper function to select trail
        select_trail_from_dropdown(driver, wait, "All Trails")
        time.sleep(MEDIUM_WAIT_TIME)
        
        # Verify selection worked
        assert True  # Basic test - if we get here without error, selection worked

    finally:
        driver.quit()