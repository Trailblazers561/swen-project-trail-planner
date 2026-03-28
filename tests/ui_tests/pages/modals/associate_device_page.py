from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium_helper import SeleniumHelper as SH

from datetime import datetime
import re
from selenium.common.exceptions import NoSuchElementException

from dtos.device_dto import DeviceDTO
from dtos.trail_dto import TrailDTO
from dtos.trail_group_dto import TrailGroupDTO
from dtos.graph_dto import GraphDTO, LineDTO, PointDTO
from dtos.trail_status_dto import TrailStatusDTO

class EditTrailPage:
    root = (By.XPATH, "//div[@data-testid='associate-device-modal']")
    unpaired_devices = (By.XPATH, "//div[@data-testid='unpaired-device-item']") #'2\nCurrently on: Giant Mountain\nBattery: 88%'
    paired_devices = (By.XPATH, "//div[@data-testid='paired-device-item']") #'2\nCurrently on: Giant Mountain\nBattery: 88%'a
    trail_select = (By.XPATH, "//select[@id='trail-select']")
    device_button_xpath = "//*[@data-testid='associate-device-id' and text()='{}']"
    associate_device_button = (By.XPATH, "associate-device-button")

    def __init__(self, driver: webdriver.Chrome):
        self.driver = driver
        SH.wait_for_element_appear(self.driver, self.root)

    def retrieve_unpaired_devices(self) -> list[DeviceDTO]:
        unpaired_text = SH.retrieve_text_from_elements(self.driver, self.unpaired_devices)

        device_list = []
        for text in unpaired_text:
            parts = text.split("\n")
            device_id = parts[0]
            battery = parts[1] if len(parts) >= 2 else ""
            device_list.append(DeviceDTO(device_id, battery=battery))

        return device_list

    def retrieve_paired_devices(self) -> list[DeviceDTO]:
        paired_text = SH.retrieve_text_from_elements(self.driver, self.paired_devices)

        device_list = []
        for text in paired_text:
            parts = text.split("\n")
            device_id = parts[0]
            trail = TrailDTO(parts[1])
            battery = parts[2] if len(parts) >= 3 else ""
            device_list.append(DeviceDTO(device_id, trail, battery))

        return device_list

    def associate_device(self, device: DeviceDTO):
        self._click_device(device.device_id)
        self._select_trail(device.current_trail)
        self._click_associate_device()

    def _click_device(self, device_id: str) -> None:
        SH.click_element(self.driver, (By.XPATH, self.associate_device_button.format(device_id)))

    def _select_trail(self, trail: TrailDTO):
        options = SH.retrieve_dropdown_options(self.driver, self.trail_select)
        correct_option = None
        for option in options:
            if re.fullmatch(rf"{re.escape(trail.trail_name)} \(ID: \d+\)", option):
                correct_option = option
                break
        if correct_option == None:
            raise NoSuchElementException(f"Cannot find option with trail_name [{trail.trail_name}]")
        SH.select_dropdown_option(self.driver, self.trail_select, correct_option)

    def _click_associate_device(self) -> None:
        SH.click_element(self.driver, self.associate_device_button)