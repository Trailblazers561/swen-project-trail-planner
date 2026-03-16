import time
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import pytest
from test_helpers import login, getService, getOptions
from ui_config import DEFAULT_WAIT_TIME, LONG_WAIT_TIME, LOGOUT_BUTTON_CLASS

@pytest.mark.UI
@pytest.mark.skip(reason="deprecated")
def test_Login_Logout():
    """Test login and logout functionality"""
    driver = webdriver.Chrome(service=getService(), options=getOptions())

    try:
        # Test login
        login(driver)

        # Verify the new URL does not contain "login" but contains "dashboard"
        current_url = driver.current_url
        assert "login" not in current_url, "User is still on the login page!"
        assert "dashboard" in current_url, "User did not log in"

        # Find and click the logout button
        wait = WebDriverWait(driver, DEFAULT_WAIT_TIME)
        logout_button = wait.until(EC.element_to_be_clickable((By.CLASS_NAME, LOGOUT_BUTTON_CLASS)))
        logout_button.click()

        # Wait for navigation
        time.sleep(LONG_WAIT_TIME)

        # Verify the new URL does not contain "dashboard" but contains "login"
        current_url = driver.current_url
        assert "login" in current_url, "User is still on the dashboard page!"
        assert "dashboard" not in current_url, "User did not log out"
    finally:
        driver.quit()