import pprint
import string

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
        frames = ['Faci' + str(number), 'Master', 'Form_Body']
        for frame in frames:
            self.driver.switch_to.frame(frame)

    def fill_input(self, id_name, value):
        find_serial = Wait(self.driver, 5).until(ec.visibility_of_element_located((By.ID, id_name)))
        find_serial.send_keys(value)

    def click_on_button(self, id_name):
        find_serial = Wait(self.driver, 5).until(ec.visibility_of_element_located((By.ID, id_name)))
        find_serial.click()

    def switch_to_child_window(self, window_title):
        for window_handle in self.driver.window_handles:
            self.driver.switch_to.window(window_handle)
            if window_title in self.driver.title:
                print('Found the child window')
                return True
        return False

    def switch_to_parent_window(self, parent_window_handle):
        self.driver.switch_to.window(parent_window_handle)

    def close_all_windows(self, parent_window_handle):
        for window_handle in self.driver.window_handles:
            if window_handle != parent_window_handle:
                self.driver.switch_to.window(window_handle)
                self.driver.close()

    def get_captcha(self):
        # TODO: this should be replace with python code instead of getting from input
        return input()

    def login(self, student_id, national_id):
        self.go_to_frame(1)
        time.sleep(1)
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

    def go_to_this_term_courses(self, available=True):
        self.go_to_102()
        self.driver.switch_to.default_content()
        self.go_to_frame(3)
        self.fill_input('GF10956_0', int(available))
        self.driver.switch_to.default_content()
        self.driver.switch_to.frame('Faci3')
        self.driver.switch_to.frame('Commander')
        self.click_on_button("IM16_ViewRep")
        time.sleep(10)

    def extract_courses(self):
        self.driver.switch_to.default_content()
        rows = self.driver.find_elements(by=By.XPATH, value='.//tr')
        data = []
        for row in rows:
            datum = []
            columns = row.find_elements(by=By.XPATH, value='.//td')
            for column in columns:
                if column.text.strip() == '':
                    datum.append(column.get_attribute('innerHTML'))
                else:
                    datum.append(column.text)
            data.append(datum)
        return data

    def get_courses(self, available=True):
        self.go_to_this_term_courses(available)
        self.driver.switch_to.default_content()
        parent_window_handle = self.driver.current_window_handle
        self.driver.switch_to.frame('Faci3')
        self.driver.switch_to.frame('Commander')
        self.click_on_button('ExToEx')
        self.switch_to_child_window(self.driver.window_handles[1])
        time.sleep(2)
        self.extract_courses()
        self.close_all_windows(parent_window_handle)
        self.switch_to_parent_window(parent_window_handle)
