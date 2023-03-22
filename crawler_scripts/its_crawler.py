from requests import Response
from bs4_crawler import BS4Crawler


class ITSCrawler(BS4Crawler):
    LOGIN_URL = 'https://cas.iust.ac.ir/auth/login?service=https%3A%2F%2Fits.iust.ac.ir%2Fuser'
    DASHBOARD_URL = 'https://its.iust.ac.ir/dash/'
    PROFILE_URL = 'https://its.iust.ac.ir/user/'

    def __init__(self):
        super().__init__()

    def login(self, username, password) -> Response | None:
        self.browser.open(self.LOGIN_URL)
        self.browser.select_form('#fm1')
        self.browser["username"] = username
        self.browser["password"] = password
        resp = self.browser.submit_selected()
        if resp.status_code == 200:
            return resp
        else:
            self.close_browser()
            return None

    def find_its_id(self):
        self.browser.open(self.DASHBOARD_URL)
        cur_url = self.browser.url
        url_parts = cur_url.split('/')
        its_id = url_parts[4]
        return its_id

    def crawl_profile_data(self):
        resp = self.browser.open(self.PROFILE_URL)
        self.browser.add_soup(response=resp, soup_config={'features': 'lxml'})
        elements = resp.soup.find_all('div', class_='profile-info-value')
        data = self.extract_data_from_elements(elements)
        data['its_id'] = self.find_its_id()
        return data

    @staticmethod
    def extract_data_from_elements(elements):
        elements = [el.text.strip() for el in elements]

        if 'نیست' in elements[11]:
            elements[11] = False
        else:
            elements[11] = True

        for i in range(12, 15):
            if 'نشده' in elements[i]:
                elements[i] = None

        if 'نشده' in elements[19]:
            elements[19] = None

        return {'persian_fullname': elements[0],
                'english_fullname': elements[1],
                'national_code': elements[2],
                'username': elements[3],
                'student_id': elements[4],
                'student_status': elements[5],
                'student_type': elements[6],
                'student_uni_email': elements[7],
                'student_department': elements[8],
                'student_email': elements[9],
                'student_phone_number': elements[10],
                'send_email_to_non_uni_email': elements[11],
                'uni_phone_number': elements[12],
                'website': elements[13],
                'fax_number': elements[14],
                'dorm': elements[15],
                'nationality': elements[16],
                'last_login': elements[17],
                'created_at': elements[18],
                'expire_date': elements[19]}
