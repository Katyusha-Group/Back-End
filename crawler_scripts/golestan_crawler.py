import time

from selenium.webdriver.common.by import By

from captcha_reader.captchaSolver import CaptchaSolver
from crawler_scripts.selenium_crawler import SeleniumCrawler
from utils import project_variables
from utils.excel_handler import ExcelHandler
import constants


class GolestanCrawler(SeleniumCrawler):
    AUTHENTICATION_URL = 'https://golestan.iust.ac.ir/forms/authenticateuser/main.htm'
    EXCEL_NAME = 'golestan_courses'

    def __init__(self, user_login, year=4012):
        super().__init__()
        self.driver.get(self.AUTHENTICATION_URL)
        self.user_login = user_login
        self.set_user_login(user_login)
        self.year = year

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
    def get_header(number):
        return ['Faci' + str(number), 'Master', 'Header']

    @staticmethod
    def get_master(number):
        return ['Faci' + str(number), 'Master']

    @staticmethod
    def get_commander(number):
        return ['Faci' + str(number), 'Commander']

    def switch_to_child_window(self, window_title):
        for window_handle in self.driver.window_handles:
            if window_title == window_handle:
                self.driver.switch_to.window(window_handle)
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
        soup = self.get_soup(self.driver.page_source)
        png_url = soup.find('img', {'id': 'imgCaptcha'})['src']
        img_path = self.image_handler.download_captcha(png_url)
        captcha_solver = CaptchaSolver()
        captcha_text = captcha_solver.get_captcha_text(img_path)
        self.image_handler.delete(img_path)
        return captcha_text

    def verify_login(self) -> bool:
        time.sleep(2)
        logged_in = self.driver.find_elements(by=By.ID, value='_mt_bou')
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
        pre_page_title = self.driver.title
        curr_page_title = self.driver.title
        while i < 5:
            if pre_page_title != curr_page_title:
                return True
            pre_page_title = curr_page_title
            curr_captcha = next_captcha
            next_captcha = self.get_captcha()
            time.sleep(1)
            self.fill_input("F51701", curr_captcha)
            if not self.user_login and i == 0:
                self.driver.find_element(by=By.XPATH, value='//*[@id="dsetting"]/label[5]').click()
            else:
                self.click_on_button("btnLog")
            time.sleep(2)
            curr_page_title = self.driver.title
            i += 1
        return False

    def go_to_102(self):
        self.switch_to_inner_frames(self.get_form_body(2))
        self.fill_input("F20851", "102")
        self.click_on_button("OK")

    def go_to_this_term_courses(self, available=True):
        if self.user_login:
            self.go_to_102()
        self.switch_to_inner_frames(self.get_form_body(self.get_number()))
        frame = (self.wait_on_find_element_by_xpath('/html/body/div[1]/div[2]/table', 10))
        element = frame.find_element(by=By.ID, value='GF07754_0')
        element.clear()
        element.send_keys(self.year)
        element = frame.find_element(by=By.ID, value='GF665530_0')
        element.clear()
        element.send_keys(4)
        time.sleep(2)
        self.driver.switch_to.default_content()
        self.switch_to_inner_frames(self.get_commander(self.get_number()))
        self.click_on_button("IM16_ViewRep")

    def extract_courses(self):
        table = self.wait_on_find_element_by_xpath('/html/body/div[1]/div[13]/table', 10)
        excel_handler = ExcelHandler()
        soup = self.get_soup(table.get_attribute('innerHTML'))
        courses = []
        rows = soup.find_all('tr')
        for row in rows:
            cols = row.find_all('td')
            for i in range(len(cols)):
                if i == 8:
                    temp = cols[i].contents
                    temp = [excel_handler.make_name_correct(temp[j].strip()) for j in range(0, len(temp), 2)]
                    cols[i] = str.join('-', temp)
                else:
                    cols[i] = cols[i].text.strip()
                    if i == 2:
                        cols[i] = cols[i].replace('/', '.')
            if cols:
                courses.append(cols)
        return courses

    def get_header_data(self):
        course_studying_group = self.wait_on_find_element_by_xpath(
            '/html/body/div[1]/div[6]/table/tbody/tr[1]/td[5]', 10).text.split(':')[1].strip()
        department = (self.wait_on_find_element_by_xpath(
            '/html/body/div[1]/div[6]/table/tbody/tr[2]/td[1]', 10).text.split(':')[1].strip())
        department_id = constants.DEPARTMENTS[department]
        course_studying_group_id = constants.COURSE_STUDYING_GP[course_studying_group]
        return [department_id, department, course_studying_group_id, course_studying_group]

    def get_courses(self, available=True):
        self.go_to_this_term_courses(available)
        time.sleep(2)
        prev_page = 0
        next_page = 1
        data = [constants.HEADER]
        while next_page == 1 or next_page != prev_page:
            self.switch_to_inner_frames(self.get_header(self.get_number()))
            self.driver.switch_to.frame(self.wait_on_find_element_by_xpath('/html/frameset/frame[2]', 10))
            header_data = self.get_header_data()
            courses_data = self.extract_courses()
            for row in courses_data:
                if row[0] != '':
                    data.append([str(self.year)] + header_data + row)
            self.switch_to_inner_frames(self.get_commander(self.get_number()))
            prev_page = next_page
            next_page = int(
                self.wait_on_find_element_by_xpath('/html/body/table/tbody/tr/td[4]/input', 10).get_attribute(
                    "value").strip())
            self.wait_on_find_element_by_xpath('/html/body/table/tbody/tr/td[5]/input', 10).click()
        if self.year == project_variables.CURRENT_SEMESTER:
            ExcelHandler().create_excel(data=data,
                                        file_name=project_variables.NEW_GOLESTAN_EXCEL_FILE_NAME + '_' + str(self.year))
        else:
            ExcelHandler().create_excel(data=data,
                                        file_name=project_variables.GOLESTAN_EXCEL_FILE_NAME + '_' + str(self.year))
