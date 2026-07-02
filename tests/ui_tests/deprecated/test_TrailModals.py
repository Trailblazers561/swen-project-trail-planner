"""
Test the Add/Edit Trail modal functionality
"""
import time
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
import pytest
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from test_helpers import login, getService, getOptions

@pytest.mark.UI
@pytest.mark.skip(reason="deprecated")
def test_AddTrailModal():
    """Test opening and interacting with the Add Trail modal"""
    driver = webdriver.Chrome(service=getService(), options=getOptions())
    
    try:
        login(driver)
        
        wait = WebDriverWait(driver, 10)
        
        # Find and click the "Add Trail" button
        add_trail_button = wait.until(EC.element_to_be_clickable((By.XPATH, "//button[contains(text(), 'Add Trail')]")))
        add_trail_button.click()
        
        time.sleep(2)
        
        # Verify modal is open - check for trail name input
        trail_name_input = wait.until(EC.presence_of_element_located((By.ID, "trail-name")))
        assert trail_name_input.is_displayed(), "Add Trail modal did not open"
        
        # Enter a trail name
        trail_name_input.clear()
        trail_name_input.send_keys("Test Trail")
        
        time.sleep(1)
        
        # Close the modal
        cancel_button = driver.find_element(By.XPATH, "//button[contains(text(), 'Cancel')]")
        cancel_button.click()
        
        time.sleep(1)
        
    finally:
        driver.quit()

@pytest.mark.UI
@pytest.mark.skip(reason="deprecated")
def test_EditTrailModal():
    """Test opening the Edit Trail Info modal"""
    driver = webdriver.Chrome(service=getService(), options=getOptions())
    
    try:
        login(driver)
        
        wait = WebDriverWait(driver, 10)
        
        # Find and click the "Edit Trail Info" button
        edit_trail_button = wait.until(EC.element_to_be_clickable((By.XPATH, "//button[contains(text(), 'Edit Trail Info')]")))
        edit_trail_button.click()
        
        time.sleep(2)
        
        # Verify modal is open - check for trail selection or input fields
        modal_content = wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, ".modal-content, [role='dialog']")))
        assert modal_content.is_displayed(), "Edit Trail Info modal did not open"
        
        # Close the modal
        cancel_button = driver.find_element(By.XPATH, "//button[contains(text(), 'Cancel')]")
        cancel_button.click()
        
        time.sleep(1)
        
    finally:
        driver.quit()