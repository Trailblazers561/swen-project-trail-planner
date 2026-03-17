"""
Test the Add/Edit Trail Group modal functionality
"""
import time
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
import pytest
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from test_helpers import login, getService, getOptions
from old_ui_config import DEFAULT_WAIT_TIME, SHORT_WAIT_TIME

@pytest.mark.UI
@pytest.mark.skip(reason="deprecated")
def test_AddGroupModal():
    """Test opening and interacting with the Add Group modal"""
    driver = webdriver.Chrome(service=getService(), options=getOptions())
    
    try:
        login(driver)
        
        wait = WebDriverWait(driver, DEFAULT_WAIT_TIME)
        
        # Find and click the "Add Group" button
        add_group_button = wait.until(EC.element_to_be_clickable((By.XPATH, "//button[contains(text(), 'Add Group')]")))
        add_group_button.click()
        
        time.sleep(SHORT_WAIT_TIME)
        
        # Verify modal is open - check for group name input
        group_name_input = wait.until(EC.presence_of_element_located((By.ID, "group-name")))
        assert group_name_input.is_displayed(), "Add Group modal did not open"
        
        # Enter a group name
        group_name_input.clear()
        group_name_input.send_keys("Test Group")
        
        time.sleep(1)
        
        # Check for checkboxes (trail selection)
        checkboxes = driver.find_elements(By.CSS_SELECTOR, "input[type='checkbox']")
        assert len(checkboxes) > 0, "No trail checkboxes found in modal"
        
        # Close the modal (click cancel or X button)
        cancel_button = driver.find_element(By.XPATH, "//button[contains(text(), 'Cancel')]")
        cancel_button.click()
        
        time.sleep(1)
        
        # Verify modal is closed
        try:
            group_name_input = driver.find_element(By.ID, "group-name")
            assert not group_name_input.is_displayed(), "Modal did not close"
        except:
            pass  # Element not found means modal is closed, which is expected
        
    finally:
        driver.quit()

@pytest.mark.UI
@pytest.mark.skip(reason="deprecated")
def test_EditGroupModal():
    """Test opening the Edit Group modal"""
    driver = webdriver.Chrome(service=getService(), options=getOptions())
    
    try:
        login(driver)
        
        wait = WebDriverWait(driver, DEFAULT_WAIT_TIME)
        
        # Find and click the "Edit Group" button
        edit_group_button = wait.until(EC.element_to_be_clickable((By.XPATH, "//button[contains(text(), 'Edit Group')]")))
        edit_group_button.click()
        
        time.sleep(SHORT_WAIT_TIME)
        
        # Verify modal is open - check for group selection dropdown or input
        # The modal should show a dropdown to select which group to edit
        modal_content = wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, ".modal-content, [role='dialog']")))
        assert modal_content.is_displayed(), "Edit Group modal did not open"
        
        # Close the modal
        cancel_button = driver.find_element(By.XPATH, "//button[contains(text(), 'Cancel')]")
        cancel_button.click()
        
        time.sleep(1)
        
    finally:
        driver.quit()