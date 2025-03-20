import time
from selenium import webdriver
from selenium.webdriver.common.by import By  # Ensure this import is present
from selenium.webdriver.common.keys import Keys
import pytest
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

@pytest.mark.UI
def test_OneTrail():
     # Initialize WebDriver
    driver = webdriver.Chrome()

    try:
        # Open the login page
        driver.get("http://trailplanner-bucket-99246436.s3-website-us-east-1.amazonaws.com")

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

        start_date = driver.find_element(By.CLASS_NAME, "date-picker-start-date") 
        start_date.send_keys("01/01/2024" + Keys.ENTER)
        time.sleep(5)
       
        # Locate the Trail dropdown and click it using JavaScript (to bypass interception)
        wait = WebDriverWait(driver, 10)  # Create an instance of WebDriverWait
        trail_selector = wait.until(EC.presence_of_element_located((By.CLASS_NAME, "trail-selector")))
        driver.execute_script("arguments[0].click();", trail_selector)

        trail_selector = wait.until(EC.presence_of_element_located((By.ID, "react-select-2-input")))
        driver.execute_script("arguments[0].click();", trail_selector)
        time.sleep(5)
        
        # Send keys directly to the dropdown
        trail_selector.send_keys("All Trails")
        trail_selector.send_keys(Keys.RETURN)  # Press Enter
        time.sleep(5)

    finally:
        # Close the browser
        driver.quit()