from selenium import webdriver

from enums.user_role import UserRole
from pages.navbar_page import NavbarPage

class RetrieveNavbarInformationStep:
    """
    Retrieves User Role and Username from Navbar
    """
    def __init__(self, driver: webdriver.Chrome):
        self.driver = driver
        self.user_role: UserRole = None
        self.username = ""

    def run(self):
        po = NavbarPage(self.driver)
        self.user_role = po.get_user_role()
        self.username = po.get_username()