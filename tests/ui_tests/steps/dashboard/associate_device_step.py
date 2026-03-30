from selenium import webdriver
from pages.dashboard_page import DashboardPage
from dtos.device_dto import DeviceDTO
from pages.modals.associate_device_page import AssociateDevicePage

class AssociateDeviceStep:
    def __init__(self, driver: webdriver.Chrome, device: DeviceDTO):
        self.driver = driver
        self.device = device

    def run(self):
        po = DashboardPage(self.driver)
        po.click_associate_device()

        po = AssociateDevicePage(self.driver)
        po.associate_device(self.device)