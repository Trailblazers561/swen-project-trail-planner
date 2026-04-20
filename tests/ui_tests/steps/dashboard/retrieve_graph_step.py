from selenium import webdriver

from dtos.graph_dto import GraphDTO
from pages.dashboard_page import DashboardPage

class RetrieveGraphStep:
    """
    Retrieves Graph From Dashboard
    """
    def __init__(self, driver: webdriver.Chrome):
        self.driver = driver
        self.graph: GraphDTO = None

    def run(self):
        po = DashboardPage(self.driver)
        self.graph = po.retrieve_graph()