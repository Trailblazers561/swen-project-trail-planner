from selenium import webdriver

from dtos.device_dto import DeviceDTO
from pages.dashboard_page import DashboardPage
from pages.modals.associate_device_page import AssociateDevicePage

class RetrieveAssociatedDevicesStep:
    """
    Retrievs List of Paired and Unpaired Devices
    """
    def __init__(self, driver: webdriver.Chrome):
        self.driver = driver
        self.unpaired_devices: list[DeviceDTO] = []
        self.paired_devices: list[DeviceDTO] = []

    def run(self):
        po = DashboardPage(self.driver)
        po.click_associate_device()

        po = AssociateDevicePage(self.driver)
        self.unpaired_devices = po.retrieve_unpaired_devices()
        self.paired_devices = po.retrieve_paired_devices()
        po.close_modal()