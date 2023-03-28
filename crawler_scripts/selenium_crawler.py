import time

from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as ec
from selenium.webdriver.support.ui import WebDriverWait as Wait

from image_handler import ImageHandler


class SeleniumCrawler:
    def __init__(self):
        self.options = webdriver.ChromeOptions()
        self.options.add_argument('--headless')
        self.options.add_argument('--disable-gpu')
        self.options.add_argument('--no-sandbox')
        self.options.add_experimental_option("detach", True)
        self.driver = webdriver.Chrome(options=self.options)

    def fill_input(self, id_name, value):
        self.driver.find_element(by=By.ID, value=id_name).clear()
        find_serial = Wait(self.driver, 5).until(ec.visibility_of_element_located((By.ID, id_name)))
        find_serial.send_keys(value)

    def click_on_button(self, id_name):
        find_serial = Wait(self.driver, 5).until(ec.visibility_of_element_located((By.ID, id_name)))
        find_serial.is_selected = False
        find_serial.click()

    def get_soup(self):
        page_source = self.driver.page_source
        soup = BeautifulSoup(page_source, 'html.parser')
        return soup

    def refresh(self):
        self.driver.refresh()
        self.driver.switch_to.alert.accept()
        time.sleep(3)
