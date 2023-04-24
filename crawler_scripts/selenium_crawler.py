import os

from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.remote.webelement import WebElement
from selenium.webdriver.support import expected_conditions as ec
from selenium.webdriver.support.ui import WebDriverWait as Wait
from webdriver_manager.chrome import ChromeDriverManager
from utils.image_handler import ImageHandler


class SeleniumCrawler:
    def __init__(self):
        self.options = webdriver.ChromeOptions()
        self.options.add_argument('--headless')
        self.options.add_argument('--disable-gpu')
        self.options.add_argument('--no-sandbox')
        self.options.add_experimental_option("detach", True)
        self.driver = webdriver.Chrome(options=self.options)
        # self.driver = webdriver.Chrome(ChromeDriverManager().install())
        # self.driver = webdriver.Chrome()
        self.image_handler = ImageHandler(os.path.abspath(os.path.join(__file__, os.pardir)) + '/captcha_images/')

    def wait_on_find_element_by_xpath(self, xpath, sleep_time) -> WebElement:
        return Wait(self.driver, sleep_time).until(ec.visibility_of_element_located((By.XPATH, xpath)))

    def wait_on_find_element_by_id(self, id_name, sleep_time) -> WebElement:
        return Wait(self.driver, sleep_time).until(ec.visibility_of_element_located((By.ID, id_name)))

    def wait_on_find_element_by_name(self, name, sleep_time) -> WebElement:
        return Wait(self.driver, sleep_time).until(ec.visibility_of_element_located((By.NAME, name)))

    def fill_input(self, id_name, value, sleep_time=10):
        element = self.wait_on_find_element_by_id(id_name, sleep_time)
        element.clear()
        element.send_keys(value)

    def click_on_button(self, id_name, sleep_time=10):
        element = self.wait_on_find_element_by_id(id_name, sleep_time)
        element.is_selected = False
        element.click()

    def get_soup(self):
        page_source = self.driver.page_source
        soup = BeautifulSoup(page_source, 'html.parser')
        return soup

    def refresh(self):
        self.driver.refresh()
        self.driver.switch_to.alert.accept()

    def remove_disable_attr(self, id_name, sleep_time=10):
        element = self.wait_on_find_element_by_id(id_name, sleep_time)
        self.driver.execute_script('arguments[0].removeAttribute("disabled");', element)
