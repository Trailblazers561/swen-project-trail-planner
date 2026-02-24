"""
Helper functions for UI tests
"""
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from webdriver_manager.chrome import ChromeDriverManager
import time
from ui_config import (
    BASE_URL, 
    LOGIN_EMAIL, 
    LOGIN_PASSWORD, 
    LONG_WAIT_TIME,
    SHORT_WAIT_TIME,
    EMAIL_FIELD_ID,
    PASSWORD_FIELD_ID,
    SIGN_IN_BUTTON_CLASS,
    TRAIL_SELECTOR_CLASS
)

def login(driver, url=None, email=None, password=None):
    """
    Helper function to log in to the application
    
    Args:
        driver: Selenium WebDriver instance
        url: Optional URL override (defaults to BASE_URL from config)
        email: Optional email override (defaults to LOGIN_EMAIL from config)
        password: Optional password override (defaults to LOGIN_PASSWORD from config)
    """
    if url is None:
        url = BASE_URL
    if email is None:
        email = LOGIN_EMAIL
    if password is None:
        password = LOGIN_PASSWORD

    driver.get(url)
    
    # Find and enter the email
    email_field = driver.find_element(By.ID, EMAIL_FIELD_ID)
    email_field.send_keys(email)
    
    # Find and enter the password
    password_field = driver.find_element(By.ID, PASSWORD_FIELD_ID)
    password_field.send_keys(password)
    
    # Find and click the sign-in button
    sign_in_button = driver.find_element(By.CLASS_NAME, SIGN_IN_BUTTON_CLASS)
    sign_in_button.click()
    
    # Wait for navigation
    time.sleep(LONG_WAIT_TIME)
    
    # Verify login was successful
    current_url = driver.current_url
    assert "dashboard" in current_url or "login" not in current_url, "Login failed"

def select_trail_from_dropdown(driver, wait, trail_name="All Trails"):
    """
    Helper function to select a trail from the react-select dropdown.
    Uses multiple strategies to find and interact with the react-select input.
    
    Args:
        driver: Selenium WebDriver instance
        wait: WebDriverWait instance
        trail_name: Name of the trail to select (defaults to "All Trails")
    """
    # Find the trail selector container by class name
    trail_selector_container = wait.until(EC.presence_of_element_located((By.CLASS_NAME, TRAIL_SELECTOR_CLASS)))
    
    # Click on the control to open the dropdown - try multiple selectors
    control_clicked = False
    control_selectors = [
        ".css-1hwfws3",  # Common react-select control class
        "[class*='control']",  # Any element with 'control' in class
        "div[class*='__control']",  # BEM-style control
    ]
    
    for selector in control_selectors:
        try:
            control = trail_selector_container.find_element(By.CSS_SELECTOR, selector)
            driver.execute_script("arguments[0].scrollIntoView(true);", control)
            driver.execute_script("arguments[0].click();", control)
            control_clicked = True
            break
        except:
            continue
    
    # If control click didn't work, try clicking the container itself
    if not control_clicked:
        driver.execute_script("arguments[0].scrollIntoView(true);", trail_selector_container)
        driver.execute_script("arguments[0].click();", trail_selector_container)
    
    time.sleep(SHORT_WAIT_TIME)
    
    # Find the input element using multiple strategies
    input_element = None
    input_selectors = [
        # Strategy 1: Find input within the trail selector container
        (By.CSS_SELECTOR, f"div.{TRAIL_SELECTOR_CLASS} input[type='text']"),
        (By.CSS_SELECTOR, f"div.{TRAIL_SELECTOR_CLASS} input[id*='react-select']"),
        (By.CSS_SELECTOR, f"div.{TRAIL_SELECTOR_CLASS} input"),
        # Strategy 2: Find by XPath
        (By.XPATH, f"//div[contains(@class, '{TRAIL_SELECTOR_CLASS}')]//input[@type='text']"),
        (By.XPATH, f"//div[contains(@class, '{TRAIL_SELECTOR_CLASS}')]//input[contains(@id, 'react-select')]"),
        # Strategy 3: Find any visible input in a menu
        (By.CSS_SELECTOR, "div[class*='menu'] input[type='text']"),
        (By.CSS_SELECTOR, "input[id*='react-select'][type='text']"),
    ]
    
    for by, selector in input_selectors:
        try:
            input_element = wait.until(EC.presence_of_element_located((by, selector)))
            # Verify it's visible and enabled
            if input_element.is_displayed() and input_element.is_enabled():
                break
        except:
            continue
    
    if input_element is None:
        raise Exception(f"Could not find react-select input for trail selector")
    
    # Clear and type the trail name
    input_element.clear()
    input_element.send_keys(trail_name)
    time.sleep(SHORT_WAIT_TIME)
    
    # Press Enter to select
    input_element.send_keys(Keys.RETURN)
    time.sleep(SHORT_WAIT_TIME)

def getService():
    return Service(ChromeDriverManager().install())

def getOptions():
    options = Options()
    options.add_argument('--headless')
    options.add_argument('--no-sandbox')
    options.add_argument('--disable-dev-shm-usage')
    options.add_argument('--disable-gpu')
    options.add_argument('--disable-extensions')
    options.add_argument('--start-maximized')
    # Memory optimization
    options.add_argument('--disk-cache-size=1')
    options.add_argument('--media-cache-size=1')
    options.add_argument('--incognito')
    options.add_argument('--remote-debugging-port=9222')
    options.add_argument('--aggressive-cache-discard')
    return options