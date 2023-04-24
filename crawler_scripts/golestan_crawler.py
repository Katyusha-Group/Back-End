from selenium.webdriver.common.by import By

from captcha_reader.captchaSolver import CaptchaSolver
from crawler_scripts.selenium_crawler import SeleniumCrawler
from utils.excel_handler import ExcelHandler
import time


class GolestanCrawler(SeleniumCrawler):
    AUTHENTICATION_URL = 'https://golestan.iust.ac.ir/forms/authenticateuser/main.htm'
    FORM_NUMBER = 2
    EXCEL_NAME = 'golestan_courses'

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
            if window_title == window_handle:
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
        time.sleep(3)
        soup = self.get_soup()
        png_url = soup.find('img', {'id': 'imgCaptcha'})['src']
        img_path = self.image_handler.download_captcha(png_url)
        captcha_solver = CaptchaSolver()
        captcha_text = captcha_solver.get_captcha_text(img_path)
        self.image_handler.delete(img_path)
        return captcha_text

    def verify_login(self) -> bool:
        time.sleep(3)
        logged_in = self.driver.find_elements(by=By.ID, value='_mt_usr')
        return len(logged_in) > 0

    def login(self) -> bool:
        """Login to Golestan Account. if login was done successfully we'll return True. else False will be returned"""
        time.sleep(2)
        self.switch_to_inner_frames(self.get_form_body(1))
        is_logged_in = self.pass_captcha()
        return is_logged_in

    def pass_captcha(self):
        time.sleep(1)
        i = 0
        next_captcha = 'a'
        is_logged_in = False
        while not is_logged_in and i < 5:
            curr_captcha = next_captcha
            next_captcha = self.get_captcha()
            self.fill_input("F51701", curr_captcha)
            if i == 0:
                self.driver.find_element(by=By.XPATH, value='//*[@id="dsetting"]/label[5]').click()
            else:
                self.click_on_button("btnLog")
            is_logged_in = self.verify_login()
            i += 1
        return is_logged_in

    def go_to_102(self):
        time.sleep(2)
        self.switch_to_inner_frames(self.get_form_body(2))
        self.fill_input("F20851", "102")
        self.click_on_button("OK")

    def go_to_this_term_courses(self, available=True):
        self.driver.switch_to.default_content()
        time.sleep(1)
        self.switch_to_inner_frames(self.get_form_body(self.FORM_NUMBER))
        self.fill_input('GF10956_0', int(available))
        self.fill_input('GF665530_0', 4)
        self.switch_to_inner_frames(self.get_commander(self.FORM_NUMBER))
        self.click_on_button("IM16_ViewRep")

    def extract_courses(self):
        time.sleep(2)
        excel_handler = ExcelHandler()
        self.driver.switch_to.default_content()
        soup = self.get_soup()
        courses = []
        rows = soup.find_all('tr')
        for row in rows:
            cols = row.find_all('td')
            cols = [ele.text.strip() for ele in cols]
            if cols:
                cols[13] = excel_handler.make_name_correct(cols[13])
                courses.append(cols)
        courses[0][1] = 'كد دانشكده درس'
        courses[0][3] = 'كد گروه آموزشی درس'
        courses[0][13] = 'نام استاد'
        excel_handler.create_excel(data=courses, file_name=self.EXCEL_NAME)

    def get_courses(self, available=True):
        self.go_to_this_term_courses(available)
        time.sleep(1)
        self.switch_to_inner_frames(frames=self.get_commander(self.FORM_NUMBER))
        self.remove_disable_attr('ExToEx', 20)
        self.click_on_button('ExToEx')
        self.switch_to_child_window(window_title=self.driver.window_handles[1])
        self.extract_courses()
        self.close_all_windows(parent_window_handle=self.driver.window_handles[0])
        self.switch_to_parent_window(parent_window_handle=self.driver.window_handles[0])
