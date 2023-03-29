from selenium.webdriver.common.by import By

from captcha_reader.captchaSolver import CaptchaSolver
from crawler_scripts.selenium_crawler import SeleniumCrawler
from crawler_scripts.excel_creator import ExcelCreator
import time


class GolestanCrawler(SeleniumCrawler):
    AUTHENTICATION_URL = 'https://golestan.iust.ac.ir/forms/authenticateuser/main.htm'

    def __init__(self, user_login, username=None, password=None):
        super().__init__()
        self.driver.get(self.AUTHENTICATION_URL)
        self.user_login = user_login
        self.set_user_login(user_login)
        self.username = username
        self.password = password

    def set_user_login(self, user_login):
        self.user_login = user_login

    def set_username(self, username):
        self.username = username

    def set_password(self, password):
        self.password = password

    def get_number(self):
        return 3 if self.user_login else 2

    def switch_to_inner_frames(self, frames):
        self.driver.switch_to.default_content()
        for frame in frames:
            element = self.wait_on_find_element_by_name(frame, 5)
            self.driver.switch_to.frame(element)

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
        time.sleep(1)
        soup = self.get_soup()
        png_url = soup.find('img', {'id': 'imgCaptcha'})['src']
        img_path = self.image_handler.download(png_url)
        captcha_solver = CaptchaSolver()
        captcha_text = captcha_solver.get_captcha_text(img_path)
        self.image_handler.delete(img_path)
        return captcha_text

    def verify_login(self) -> bool:
        time.sleep(1)
        logged_in = self.driver.find_elements(by=By.ID, value='_mt_usr')
        return len(logged_in) > 0

    def login(self) -> bool:
        """Login to Golestan Account. if login was done successfully we'll return True. else False will be returned"""
        if self.user_login:
            return self.login_user()
        else:
            return self.login_admin()

    def login_user(self):
        self.switch_to_inner_frames(self.get_form_body(1))
        self.fill_input("F80351", self.username)
        self.fill_input("F80401", self.password)
        is_logged_in = self.pass_captcha()
        return is_logged_in

    def login_admin(self) -> bool:
        self.switch_to_inner_frames(self.get_form_body(1))
        is_logged_in = self.pass_captcha()
        return is_logged_in

    def pass_captcha(self):
        time.sleep(3)
        i = 0
        next_captcha = 'a'
        is_logged_in = False
        while not is_logged_in and i < 5:
            curr_captcha = next_captcha
            next_captcha = self.get_captcha()
            self.fill_input("F51701", curr_captcha)
            if not self.user_login and i == 0:
                self.driver.find_element(by=By.XPATH, value='//*[@id="dsetting"]/label[5]').click()
            else:
                self.click_on_button("btnLog")
            is_logged_in = self.verify_login()
            i += 1
        return is_logged_in

    def go_to_102(self):
        self.switch_to_inner_frames(self.get_form_body(2))
        self.fill_input("F20851", "102")
        self.click_on_button("OK")

    def go_to_this_term_courses(self, available=True):
        if self.user_login:
            self.go_to_102()
        self.driver.switch_to.default_content()
        self.switch_to_inner_frames(self.get_form_body(self.get_number()))
        self.fill_input('GF10956_0', int(available))
        self.switch_to_inner_frames(self.get_commander(self.get_number()))
        self.click_on_button("IM16_ViewRep")

    def extract_courses(self):
        time.sleep(2)
        self.driver.switch_to.default_content()
        soup = self.get_soup()
        courses = []
        rows = soup.find_all('tr')
        for row in rows:
            cols = row.find_all('td')
            cols = [ele.text.strip() for ele in cols]
            if cols:
                courses.append(cols)
        suffix = '_captcha' if not self.user_login else ''
        excel_creator = ExcelCreator(courses, f'golestan_courses{suffix}.xlsx')
        excel_creator.create_excel()

    def get_courses(self, available=True):
        self.go_to_this_term_courses(available)
        self.switch_to_inner_frames(frames=self.get_commander(self.get_number()))
        if not self.user_login:
            self.remove_disable_attr('ExToEx', 20)
        self.click_on_button('ExToEx')
        self.switch_to_child_window(window_title=self.driver.window_handles[1])
        self.extract_courses()
        self.close_all_windows(parent_window_handle=self.driver.window_handles[0])
        self.switch_to_parent_window(parent_window_handle=self.driver.window_handles[0])
