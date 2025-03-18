import time
from selenium import webdriver
from selenium.webdriver.common.by import By  # Ensure this import is present
from selenium.webdriver.common.keys import Keys
import pytest

@pytest.mark.UI
def test_Login_Logout():
    # Initialize WebDriver
    driver = webdriver.Chrome()

    try:
        # Open the login page
        driver.get("http://trailplanner-bucket-94542823.s3-website-us-east-1.amazonaws.com")

        # Find and enter the email
        email_field = driver.find_element(By.ID, "email")  
        email_field.send_keys("admin@gmail.com")

        # Find and enter the password
        password_field = driver.find_element(By.ID, "password")  
        password_field.send_keys("password")

        # Find and click the sign-in button
        sign_in_button = driver.find_element(By.CLASS_NAME, "button-3d")  
        sign_in_button.click()

        # Wait for 5 seconds to allow navigation
        time.sleep(5)

        # Verify the new URL does not contain "login" but contains "dashboard"
        current_url = driver.current_url
        assert "login" not in current_url, "User is still on the login page!"
        assert "dashboard" in current_url, "User did not log in"

        # Find and click the logout button
        logout_button = driver.find_element(By.CLASS_NAME, "logout-button")  
        logout_button.click()

        # Wait for 5 seconds to allow navigation
        time.sleep(5)

        # Verify the new URL does not contain "dashboard" but contains "login"
        current_url = driver.current_url
        assert "login" in current_url, "User is still on the dashboard page!"
        assert "dashboard" not in current_url, "User did not log out"
    finally:
        # Close the browser
        driver.quit()