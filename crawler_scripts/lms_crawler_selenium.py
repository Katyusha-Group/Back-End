import os
import time

import pandas as pd
from selenium.webdriver.common.by import By

from crawler_scripts.image_handler import ImageHandler
from crawler_scripts.selenium_crawler import SeleniumCrawler


class LMSCrawlerSelenium(SeleniumCrawler):
    LOGIN_URL = 'https://lms.iust.ac.ir/login/index.php'
    LOGIN_XPATH_BUTTON = '/html/body/div[4]/div/div/div/section/div/div[2]/div/div/div/div/div/div/div/div/a'
    TEACHER_IMG_XPATH = '/html/body/img'
    AUTHENTICATION_URL = 'https://its.iust.ac.ir/oauth2/autheticate'
    TEACHERS_INFO_EXCEL = '../data/teachers_info.xlsx'
    TEACHER_IMAGE_PATH = '../media/teachers_images/'

    def __init__(self):
        super().__init__()
        self.image_handler = ImageHandler(os.path.abspath(os.path.join(__file__, os.pardir)) + '/teacher_images/')

    def login(self, username, password):
        print('Logging in')
        self.driver.get(self.LOGIN_URL)
        time.sleep(1)
        url = (self.driver.find_element(by=By.XPATH, value=self.LOGIN_XPATH_BUTTON)
               ).get_attribute('href')
        self.driver.get(url)
        self.fill_input(id_name='edit-name', value=username)
        self.fill_input(id_name='edit-pass', value=password)
        self.click_on_button(id_name='edit-submit')

    def get_teachers_photo(self, start, count):
        print("Getting teachers' profile image")
        data = self.get_img_urls()
        for i in range(start, min(start + count, len(data))):
            self.driver.get(data[i][0])
            try:
                self.wait_on_find_element_by_xpath(self.TEACHER_IMG_XPATH, sleep_time=1).screenshot(
                    self.TEACHER_IMAGE_PATH + str(data[i][1]) + '.png')
            except:
                pass

    def get_img_urls(self):
        data = pd.read_excel(self.TEACHERS_INFO_EXCEL)
        data = pd.DataFrame(data=data.iloc[:, [2, 3]]).values
        return data
