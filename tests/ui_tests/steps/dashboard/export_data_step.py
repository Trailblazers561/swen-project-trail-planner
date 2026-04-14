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

        time.sleep(10)
        self.driver.save_screenshot(Path(__file__).resolve().parents[2] / f"errors/import_export_data_step_{int(time.time())}.png")
        found = False
        found_where = ""
        for root, dirs, files in os.walk("/"):
            if "trail_data.csv" in files:
                print("FOUND DOWNLOAD AT:", os.path.join(root, "trail_data.csv"))
                found_where = os.path.join(root, "trail_data.csv")
                self.export_file_path = found_where
        if found:
            with open(found_where) as f:
                for line in f:
                    print("LINEEE",line)
        else:
            print("NOT FOUND FILE CALLED trail_data.csv")

        # start_time = time.time()
        # while True:
        #     if trail_file_path.exists():
        #         self.export_file_path = trail_file_path
        #         break
        #     if time.time() - start_time > 15:
        #         break
        #     time.sleep(.5)

