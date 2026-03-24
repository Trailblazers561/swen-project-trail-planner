from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium_helper import SeleniumHelper as SH

from datetime import datetime

from dtos.dashboard_filter_dto import DashboardFilterDTO
from dtos.trail_dto import TrailDTO
from dtos.trail_group_dto import TrailGroupDTO
from dtos.graph_dto import GraphDTO, LineDTO, PointDTO
from dtos.trail_status_dto import TrailStatusDTO

class DashboardPage:
    root = (By.XPATH, "//div[@data-testid='dashboard-root']")
    #Dashboard Headers
    date_range_picker = (By.XPATH, "//button[@id='date-picker-range']")
    date_calandar_popup = (By.XPATH, "//div[@data-testid='calandar-popup']")
    first_month_label = (By.XPATH, "(//div[@data-testid='calandar-popup']/div/div/div)[1]//span[@role='status']")
    previous_month_button = (By.XPATH, "//button[@aria-label='Go to the Previous Month']")
    next_month_button = (By.XPATH, "//button[@aria-label='Go to the Next Month']")
    day_xpath = "(//div[@data-testid='calandar-popup']/div/div/div)[1]//td[@data-day='{}']"
    trails_dropdown = (By.XPATH, "//button[@data-testid='trail-selector']")
    selected_trails = (By.XPATH, trails_dropdown[1] + "//span[@data-slot='badge']")
    trail_groups_dropdown = (By.XPATH, "//button[@data-testid='trail-group-selector']")
    selected_trail_groups = (By.XPATH, trail_groups_dropdown[1] + "//span[@data-slot='badge']")
    trail_dropdown_option_xpath = "//div[@data-value='{}']"
    dropdown_clear = (By.XPATH, trail_dropdown_option_xpath.format("Clear"))
    dropdown_close = (By.XPATH, trail_dropdown_option_xpath.format("Close"))
    associate_device_button = (By.XPATH, "//button[@data-testid='associate-device']")
    export_data_button = (By.XPATH, "//button[@data-testid='export-data']")
    import_data_button = (By.XPATH, "//button[@data-testid='import-data']")
    # Trail Options
    toggle_view_button = (By.XPATH, "//button[@data-testid='toggle-view']")
    table_graph_root = (By.XPATH, "(//div[@data-testid='trail-status-table']//div[@role='table']/div)[1] | //h2[@data-testid='graph-title']")
    trail_options_button = (By.XPATH, "//button[@data-testid='trail-options']")
    add_trail_options_button = (By.XPATH, "//div[@data-testid='add-trail']")
    edit_trail_options_button = (By.XPATH, "//div[@data-testid='edit-trail']")
    trail_group_options_button = (By.XPATH, "//button[@data-testid='trail-group-options']")
    add_group_options_button = (By.XPATH, "//div[@data-testid='add-trail-group']")
    edit_group_options_button = (By.XPATH, "//div[@data-testid='edit-trail-group']")
    # Graph View
    graph_title_label = (By.XPATH, "//h2[@data-testid='graph-title']")
    graph = (By.XPATH, "//div[@data-testid='outer-dashboard-graph']/div")
    # Trail Status View
    table_root = "//div[@data-testid='trail-status-table']"
    table_head = table_root + "//div[contains(@class, 'TableHead')]"
    trail_name_header = (By.XPATH, table_head + "//div[@data-column-id='1']")
    weekly_count_header = (By.XPATH, table_head + "//div[@data-column-id='2']")
    battery_status_header = (By.XPATH, table_head + "//div[@data-column-id='3']")
    last_updated_header = (By.XPATH, table_head + "//div[@data-column-id='4']")
    table_body = table_root + "//div[contains(@class, 'TableBody')]"
    trail_name_labels = (By.XPATH, table_body + "//div[@data-column-id='1']")
    weekly_count_labels = (By.XPATH, table_body + "//div[@data-column-id='2']")
    battery_status_labels = (By.XPATH, table_body + "//div[@data-column-id='3']")
    last_updated_labels = (By.XPATH, table_body + "//div[@data-column-id='4']")
    rows_per_page_dropdown = (By.XPATH, "//select[@aria-label='Rows per page:']")
    first_page_button = (By.XPATH, "//button[@aria-label='First Page']")
    previous_page_button = (By.XPATH, "//button[@aria-label='Previous Page']")
    next_page_button = (By.XPATH, "//button[@aria-label='Next Page']")
    last_page_button = (By.XPATH, "//button[@aria-label='Last Page']")

    def __init__(self, driver: webdriver.Chrome):
        self.driver = driver
        SH.wait_for_element_appear(self.driver, self.root)

    def set_dashboard_filters(self, filter: DashboardFilterDTO) -> None:
        if filter.date_start != None:
            self._set_date_range(filter.date_start, filter.date_end)
        self._select_trails(filter.trails)
        self._select_trail_groups(filter.trail_groups)

    def retrieve_dashboard_filters(self) -> DashboardFilterDTO:
        date_range = SH.retrieve_text_from_element(self.driver, self.date_range_picker)
        dates = date_range.split(" - ")
        date_start = datetime.strptime(dates[0], "%b %d %Y")
        date_end = datetime.strptime(dates[1], "%b %d %Y")
        trails = {TrailDTO(trail_name) for trail_name in SH.retrieve_text_from_elements(self.driver, self.selected_trails)}
        trail_groups = {TrailGroupDTO(group_name) for group_name in SH.retrieve_text_from_elements(self.driver, self.selected_trail_groups)}
        return DashboardFilterDTO(date_start, date_end, trails, trail_groups)

    def _set_date_range(self, start: datetime, end: datetime) -> None:
        SH.click_element(self.driver, self.date_range_picker)
        SH.wait_for_element_appear(self.driver, self.date_calandar_popup)

        def click_date(target: datetime):
            while (True):
                current_month_year = datetime.strptime(SH.retrieve_text_from_element(self.driver, self.first_month_label), "%B %Y")
                if (target.year, target.month) < (current_month_year.year, current_month_year.month):
                    SH.click_element(self.driver, self.previous_month_button)
                elif (target.year, target.month) < (current_month_year.year, current_month_year.month):
                    SH.click_element(self.driver, self.next_month_button)
                else:
                    break
                SH.wait(.05)
            SH.click_element(self.driver, (By.XPATH, self.day_xpath.format(target.strftime("%Y-%m-%d"))))

        click_date(start)
        if end != None:
            click_date(end)

        SH.click_element(self.driver, self.date_range_picker)
        SH.wait_for_element_disappear(self.driver, self.date_calandar_popup)

    def _select_trails(self, trails: list[TrailDTO]) -> None:
        SH.click_element(self.driver, self.trails_dropdown)
        SH.wait(.2)
        if SH.is_element_visible(self.driver, self.dropdown_clear):
            SH.click_element(self.driver, self.dropdown_clear)
        for trail in trails:
            SH.click_element(self.driver, (By.XPATH, self.trail_dropdown_option_xpath.format(trail.trail_name)))
        SH.click_element(self.driver, self.dropdown_close)

    def _select_trail_groups(self, trail_groups: list[TrailGroupDTO]) -> None:
        SH.click_element(self.driver, self.trail_groups_dropdown)
        SH.wait(.2)
        if SH.is_element_visible(self.driver, self.dropdown_clear):
            SH.click_element(self.driver, self.dropdown_clear)
        for group in trail_groups:
            SH.click_element(self.driver, (By.XPATH, self.trail_dropdown_option_xpath.format(group.group_name)))
        SH.click_element(self.driver, self.dropdown_close)

    def click_associate_device(self) -> None:
        SH.click_element(self.driver, self.associate_device_button)

    def click_export_data(self) -> None:
        SH.click_element(self.driver, self.export_data_button)

    def click_import_data(self) -> None:
        SH.click_element(self.driver, self.import_data_button)

    def click_toggle_view(self) -> None:
        SH.click_element(self.driver, self.toggle_view_button)
        SH.wait(.5)
        SH.wait_for_element_appear(self.driver, self.table_graph_root, 10)

    def click_add_trail(self) -> None:
        SH.click_element(self.driver, self.trail_options_button)
        SH.click_element(self.driver, self.add_trail_options_button)

    def click_edit_trail(self) -> None:
        SH.click_element(self.driver, self.trail_options_button)
        SH.click_element(self.driver, self.edit_trail_options_button)

    def click_add_trail_group(self) -> None:
        SH.click_element(self.driver, self.trail_group_options_button)
        SH.click_element(self.driver, self.add_group_options_button)

    def click_edit_trail_group(self) -> None:
        SH.click_element(self.driver, self.trail_group_options_button)
        SH.click_element(self.driver, self.edit_group_options_button)

    def retrieve_graph(self) -> GraphDTO:
        title = SH.retrieve_text_from_element(self.driver, self.graph_title_label)
        lines = self.driver.execute_script("return document.querySelector('.js-plotly-plot').data")
        line_set = set()
        for line in lines:
            points = set()
            for x, y in zip(line["x"], line["y"]):
                points.add(PointDTO(datetime.fromisoformat(x), y))
            line_set.add(LineDTO(line["name"], points))
        return GraphDTO(title, line_set)

    def retrieve_trail_status(self, max=-1) -> list[TrailStatusDTO]:
        self.select_rows_per_page(30)

        if SH.retrieve_element_attribute(self.driver, self.first_page_button, "disabled") == None:
            SH.click_element(self.driver, self.first_page_button)

        trail_status_list = []
        while ((len(trail_status_list) < max) or (max == -1)):
            trail_names = SH.retrieve_text_from_elements(self.driver, self.trail_name_labels)
            weekly_counts = SH.retrieve_text_from_elements(self.driver, self.weekly_count_labels)
            battery_statuses = SH.retrieve_text_from_elements(self.driver, self.battery_status_labels)
            last_updateds = SH.retrieve_text_from_elements(self.driver, self.last_updated_labels)
            for trail_name, weekly_count, battery_status, last_updated in zip(trail_names, weekly_counts, battery_statuses, last_updateds):
                if last_updated == "N/A":
                    last_updated = None
                else:
                    last_updated = datetime.strptime(last_updated, "%m/%d/%Y")
                trail_status_list.append(TrailStatusDTO(trail_name, int(weekly_count), battery_status, last_updated))
                if len(trail_status_list) == max:
                    return trail_status_list

            if not SH.retrieve_element_attribute(self.driver, self.next_page_button, "disabled"):
                SH.click_element(self.driver, self.next_page_button)
            else:
                return trail_status_list

        if max == -1:
            return trail_status_list

        return trail_status_list[:max]

    def select_rows_per_page(self, rows: int) -> None:
        SH.select_dropdown_option(self.driver, self.rows_per_page_dropdown, str(rows))