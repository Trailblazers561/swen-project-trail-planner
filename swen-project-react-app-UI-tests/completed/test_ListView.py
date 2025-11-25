"""
Test the list view functionality
"""
import time
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
import pytest
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from test_helpers import login
from config import DEFAULT_WAIT_TIME, MEDIUM_WAIT_TIME, FILTER_CONTAINER_CLASS

@pytest.mark.UI
def test_SwitchToListView():
    """Test switching from graph view to list view"""
    driver = webdriver.Chrome()
    
    try:
        login(driver)
        
        # Find and click the "Switch to List View" button
        wait = WebDriverWait(driver, DEFAULT_WAIT_TIME)
        switch_button = wait.until(EC.presence_of_element_located((By.XPATH, "//button[contains(text(), 'Switch to List View')]")))
        switch_button.click()
        
        time.sleep(MEDIUM_WAIT_TIME)
        
        # Verify we're in list view - check for "Trail Status Overview" heading
        overview_heading = wait.until(EC.presence_of_element_located((By.XPATH, "//h2[contains(text(), 'Trail Status Overview')]")))
        assert overview_heading.is_displayed(), "List view heading not found"
        
        # Verify the button text changed to "Switch to Graph View"
        switch_button = driver.find_element(By.XPATH, "//button[contains(text(), 'Switch to Graph View')]")
        assert switch_button.is_displayed(), "Button did not update to 'Switch to Graph View'"
        
    finally:
        driver.quit()

@pytest.mark.UI
def test_ListViewTableDisplay():
    """Test that the list view table displays correctly"""
    driver = webdriver.Chrome()
    
    try:
        login(driver)
        
        # Switch to list view
        wait = WebDriverWait(driver, DEFAULT_WAIT_TIME)
        switch_button = wait.until(EC.presence_of_element_located((By.XPATH, "//button[contains(text(), 'Switch to List View')]")))
        switch_button.click()
        
        time.sleep(5)  # Wait for data to load
        
        # Check for table headers
        trail_name_header = wait.until(EC.presence_of_element_located((By.XPATH, "//th[contains(text(), 'Trail Name')]")))
        weekly_count_header = wait.until(EC.presence_of_element_located((By.XPATH, "//th[contains(text(), 'Weekly Count')]")))
        battery_status_header = wait.until(EC.presence_of_element_located((By.XPATH, "//th[contains(text(), 'Battery Status')]")))
        last_updated_header = wait.until(EC.presence_of_element_located((By.XPATH, "//th[contains(text(), 'Last Updated')]")))
        
        assert trail_name_header.is_displayed(), "Trail Name header not found"
        assert weekly_count_header.is_displayed(), "Weekly Count header not found"
        assert battery_status_header.is_displayed(), "Battery Status header not found"
        assert last_updated_header.is_displayed(), "Last Updated header not found"
        
        # Check that table rows exist (at least one trail should be displayed)
        time.sleep(2)
        table_rows = driver.find_elements(By.CSS_SELECTOR, "tbody tr")
        assert len(table_rows) > 0, "No trail rows found in table"
        
    finally:
        driver.quit()

@pytest.mark.UI
def test_SwitchBackToGraphView():
    """Test switching back from list view to graph view"""
    driver = webdriver.Chrome()
    
    try:
        login(driver)
        
        wait = WebDriverWait(driver, DEFAULT_WAIT_TIME)
        
        # Switch to list view first
        switch_button = wait.until(EC.presence_of_element_located((By.XPATH, "//button[contains(text(), 'Switch to List View')]")))
        switch_button.click()
        time.sleep(MEDIUM_WAIT_TIME)
        
        # Switch back to graph view
        switch_button = wait.until(EC.presence_of_element_located((By.XPATH, "//button[contains(text(), 'Switch to Graph View')]")))
        switch_button.click()
        time.sleep(MEDIUM_WAIT_TIME)
        
        # Verify we're back in graph view - check for graph element or filter container
        filter_container = wait.until(EC.presence_of_element_located((By.CLASS_NAME, FILTER_CONTAINER_CLASS)))
        assert filter_container.is_displayed(), "Graph view filter container not found"
        
        # Verify the button text changed back
        switch_button = driver.find_element(By.XPATH, "//button[contains(text(), 'Switch to List View')]")
        assert switch_button.is_displayed(), "Button did not update back to 'Switch to List View'"
        
    finally:
        driver.quit()