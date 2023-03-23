from selenium.webdriver.common.by import By

from captcha_reader.captchaSolver import CaptchaSolver
from crawler_scripts.selenium_crawler import SeleniumCrawler
from crawler_scripts.excel_creator import ExcelCreator
import time


class GolestanCrawler(SeleniumCrawler):
    AUTHENTICATION_URL = 'https://golestan.iust.ac.ir/forms/authenticateuser/main.htm'

    def __init__(self):
        super().__init__()
        self.driver.get(self.AUTHENTICATION_URL)

    def switch_to_inner_frames(self, frames):
        self.driver.switch_to.default_content()
        for frame in frames:
            self.driver.switch_to.frame(frame)

    @staticmethod
    def get_form_body(number):
        return ['Faci' + str(number), 'Master', 'Form_Body']

    @staticmethod
    def get_commander(number):
        return ['Faci' + str(number), 'Commander']

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
        soup = self.get_soup()
        png_url = soup.find('img', {'id': 'imgCaptcha'})['src']
        img_path = self.image_handler.download(png_url)
        captcha_solver = CaptchaSolver()
        captcha_text = captcha_solver.get_captcha_text(img_path)
        self.image_handler.delete(img_path)
        return captcha_text

    def verify_login(self) -> bool:
        logged_in = self.driver.find_elements(by=By.ID, value='_mt_usr')
        return len(logged_in) > 0

    def login(self, student_id, national_id) -> bool:
        """Login to Golestan Account. if login was done successfully we'll return True. else False will be returned"""
        time.sleep(2)
        self.switch_to_inner_frames(self.get_form_body(1))
        self.fill_input("F80351", student_id)
        self.fill_input("F80401", national_id)
        is_logged_in = False
        i = 0
        next_captcha = 'a'
        while not is_logged_in and i < 5:
            time.sleep(2)
            curr_captcha = next_captcha
            next_captcha = self.get_captcha()
            self.fill_input("F51701", curr_captcha)
            self.click_on_button("btnLog")
            time.sleep(2)
            is_logged_in = self.verify_login()
            i += 1
        return is_logged_in

    def go_to_102(self):
        self.switch_to_inner_frames(self.get_form_body(2))
        self.fill_input("F20851", "102")
        self.click_on_button("OK")
        time.sleep(2)

    def go_to_this_term_courses(self, available=True):
        self.go_to_102()
        self.driver.switch_to.default_content()
        self.switch_to_inner_frames(self.get_form_body(3))
        self.fill_input('GF10956_0', int(available))
        self.switch_to_inner_frames(self.get_commander(3))
        self.click_on_button("IM16_ViewRep")
        time.sleep(4)

    def extract_courses(self):
        self.driver.switch_to.default_content()
        soup = self.get_soup()
        courses = []
        rows = soup.find_all('tr')
        for row in rows:
            cols = row.find_all('td')
            cols = [ele.text.strip() for ele in cols]
            if cols:
                courses.append([ele for ele in cols if ele])
        excel_creator = ExcelCreator(courses, 'golestan_courses.xlsx')
        excel_creator.create_excel()

    def get_courses(self, available=True):
        self.go_to_this_term_courses(available)
        self.switch_to_inner_frames(frames=self.get_commander(3))
        self.click_on_button('ExToEx')
        self.switch_to_child_window(window_title=self.driver.window_handles[1])
        time.sleep(1)
        self.extract_courses()
        self.close_all_windows(parent_window_handle=self.driver.window_handles[0])
        self.switch_to_parent_window(parent_window_handle=self.driver.window_handles[0])
        time.sleep(2)

