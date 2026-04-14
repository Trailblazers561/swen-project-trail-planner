from selenium import webdriver

from pathlib import Path
import time

from pages.dashboard_page import DashboardPage

import os

class ExportDataStep:
    def __init__(self, driver: webdriver.Chrome):
        self.driver = driver
        self.export_file_path: Path = None

    def run(self):
        trail_file_path = Path(__file__).resolve().parents[2] / "downloads" / "trail_data.csv"
        if trail_file_path.exists():
            trail_file_path.unlink()
        po = DashboardPage(self.driver)
        po.click_export_data()

        start_time = time.time()
        while True:
            if trail_file_path.exists():
                self.export_file_path = trail_file_path
                break
            if time.time() - start_time > 15:
                break
            time.sleep(.5)

