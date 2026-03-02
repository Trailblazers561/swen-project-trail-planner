from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver import ActionChains
from selenium.webdriver.support.ui import Select
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from webdriver_manager.chrome import ChromeDriverManager
import time

from ui_config import BASE_URL

DEFAULT_WAIT = 2

class SeleniumHelper:
    # @staticmethod
    def get_driver() -> webdriver.Chrome:
        service = Service(ChromeDriverManager().install())

        options = Options()
        # options.add_argument('--headless')
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

        driver = webdriver.Chrome(service=service, options=options)
        driver.get(BASE_URL)
        return driver

    # @staticmethod
    def wait_for_element_appear(driver: webdriver.Chrome, locator: tuple[str, str], timeout: float = DEFAULT_WAIT) -> None:
        print(f"Waiting for element {locator} to appear for {timeout} seconds")
        wait = WebDriverWait(driver, timeout)
        wait.until(EC.visibility_of_element_located(locator))

    # @staticmethod
    def wait_for_element_disappear(driver: webdriver.Chrome, locator: tuple[str, str], timeout: float=DEFAULT_WAIT) -> None:
        print(f"Waiting for element {locator} to disappear for {timeout} seconds")
        wait = WebDriverWait(driver, timeout)
        wait.until(EC.invisibility_of_element_located(locator))

    # @staticmethod
    def is_element_visible(driver: webdriver.Chrome, locator: tuple[str, str]) -> bool:
        print(f"Checking if element {locator} is visible")
        try:
            element = driver.find_element(*locator)
            visible = element.is_displayed()
        except:
            visible = False
        return visible

    # @staticmethod
    def enter_text_to_element(driver: webdriver.Chrome, locator: tuple[str, str], text: str) -> None:
        print(f"Entering into element {locator} the text: {text}")
        element = driver.find_element(*locator)
        element.clear()
        element.send_keys(text)

    # @staticmethod
    def retrieve_text_from_element(driver: webdriver.Chrome, locator: tuple[str, str]) -> str:
        print(f"Retrieving text from element {locator}")
        element = driver.find_element(*locator)
        return element.text

    # @staticmethod
    def select_dropdown_option(driver: webdriver.Chrome, locator: tuple[str, str], option: str) -> None:
        print(f"Selecting element {locator} dropdown option {option}")
        element = driver.find_element(*locator)
        select = Select(element)
        try:
            select.select_by_visible_text(option)
        except:
            select.select_by_value(option)

    # @staticmethod
    def retrieve_dropdown_options(driver: webdriver.Chrome, locator: tuple[str, str]) -> list[str]:
        print(f"Retrieving element {locator} dropdown options")
        element = driver.find_element(*locator)
        select = Select(element)
        return [option.text for option in select.options]

    # @staticmethod
    def click_element(driver: webdriver.Chrome, locator: tuple[str, str]) -> None:
        print(f"Clicking on element {locator}")
        element = driver.find_element(*locator)
        element.click()

    # @staticmethod
    def hover_element(driver: webdriver.Chrome, locator: tuple[str, str]) -> None:
        print(f"Hovering over element {locator}")
        element = driver.find_element(*locator)
        actions = ActionChains(driver)
        actions.move_to_element(element).perform()

    # @staticmethod
    def retrieve_element_attribute(driver: webdriver.Chrome, locator: tuple[str, str], attribute: str) -> str:
        print(f"Retrieving element {locator} attribute {attribute}")
        element = driver.find_element(*locator)
        return element.get_attribute(attribute)

    # @staticmethod
    def dismiss_alert(driver: webdriver.Chrome) -> str:
        print(f"Dismissing alert")
        wait = WebDriverWait(driver, timeout=DEFAULT_WAIT)
        alert = wait.until(lambda d : d.switch_to.alert)
        text = alert.text
        alert.dismiss()
        return text

    # @staticmethod
    def upload_file(driver: webdriver.Chrome, locator: tuple[str, str], file_path: str):
        print(f"Uploading file to element {locator} with path {file_path}")
        # Not sure if this is actually needed (enter text might work maybe), will implement when UI gains upload functionalty.
        raise NotImplementedError

    def wait(duration: float):
        time.sleep(duration)

    
