import pprint

from selenium.webdriver.remote.webelement import WebElement
from selenium.webdriver.support.ui import WebDriverWait as Wait
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as ec
from crawler_scripts.crawler import Crawler
import time


class GolestanCrawler(Crawler):
    def __init__(self):
        super().__init__()
        self.driver.get('https://golestan.iust.ac.ir/forms/authenticateuser/main.htm')

    def go_to_frame(self, number):
        frames = ['Faci'+str(number), 'Master', 'Form_Body']
        for frame in frames:
            self.driver.switch_to.frame(frame)

    def fill_input(self, id_name, value):
        find_serial = Wait(self.driver, 5).until(ec.visibility_of_element_located((By.ID, id_name)))
        find_serial.send_keys(value)

    def click_on_button(self, id_name):
        find_serial = Wait(self.driver, 5).until(ec.visibility_of_element_located((By.ID, id_name)))
        find_serial.click()

    def get_captcha(self):
        # TODO: this should be replace with python code instead of getting from input
        return input()

    def login(self, student_id, national_id):
        self.go_to_frame(1)
        self.fill_input("F80351", student_id)
        self.fill_input("F80401", national_id)
        captcha = self.get_captcha()
        self.fill_input("F51701", captcha)
        self.click_on_button("btnLog")
        time.sleep(5)

    def go_to_102(self):
        self.go_to_frame(2)
        self.fill_input("F20851", "102")
        self.click_on_button("OK")
        time.sleep(5)

    def get_courses(self, available=True):
        self.go_to_102()
        self.driver.switch_to.default_content()
        self.go_to_frame(3)
        self.fill_input('GF10956_0', int(available))
        self.driver.switch_to.default_content()
        self.driver.switch_to.frame('Faci3')
        self.driver.switch_to.frame('Commander')
        self.click_on_button("IM16_ViewRep")
        time.sleep(5)
