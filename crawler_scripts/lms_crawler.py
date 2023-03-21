from bs4 import BeautifulSoup
import requests
from requests import Response


class LMSCrawler:
    LOGIN_URL = 'https://lms.iust.ac.ir/login/index.php'
    AUTHENTICATION_URL = 'https://its.iust.ac.ir/oauth2/autheticate'
    BASE_COURSE_VIEW_LINK = 'https://lms.iust.ac.ir/course/view.php?id='
    BASE_COURSE_INFO_LINK = 'https://lms.iust.ac.ir/course/info.php?id='

    def __init__(self):
        self.soup = None
        self.session = requests.session()

    @staticmethod
    def get_login_data(username, password) -> dict:
        return {
            'name': username,
            "pass": password,
            "form_id": "oauth2_server_authenticate_form",
        }

    def login(self, username, password) -> Response | None:
        response = self.session.get(self.LOGIN_URL)
        self.soup = BeautifulSoup(response.text, 'html.parser')
        url = self.soup.find(class_="btn btn-primary btn-block")['href']
        self.session.get(url)
        data = self.get_login_data(username, password)
        response = self.session.post(self.AUTHENTICATION_URL, data=data)
        if response.status_code == 200:
            return response
        else:
            return None

    def find_user_courses(self, all_terms=False):
        """
        Using this method we can get data about user's courses. this data can be from this term's courses or
        previous terms' courses.
        fields of data: {"id": course_lms_id, "term": course_term,
                        "view_link": course_view_link, "info_link": course_info_link,
                        "is_active": course_is_active, "days": days_list, "clock": course_clock_time,
                        "teacher_lms_id"}
        """
        response = self.session.get('https://lms.iust.ac.ir/user/profile.php')
        self.soup = BeautifulSoup(response.text, 'html.parser')

        courses_dict = {}
        courses = self.soup.find('li', class_="contentnode courseprofiles").find_all('a')
        if all_terms:
            response = self.session.get(courses[-1]['href'])
            self.soup = BeautifulSoup(response.text, 'html.parser')
            courses = self.soup.find('li', class_="contentnode courseprofiles").find_all('a')
        else:
            courses = [course for course in courses if course.span]

        for course in courses:
            course_name, course_info = self.get_course_info(course)
            days_list, clock, is_active = self.get_date_time_for_course(course_info['view_link'], all_terms)
            course_info['days'] = days_list
            course_info['clock'] = clock
            course_info['is_active'] = is_active
            teacher_lms_id = self.get_course_teacher_id(course_info['info_link'])
            course_info['teacher_lms_id'] = teacher_lms_id
            courses_dict[course_name] = course_info

        return courses_dict

    def get_date_time_for_course(self, view_link, all_terms):
        response = self.session.get(view_link)
        self.soup = BeautifulSoup(response.text, 'html.parser')
        if all_terms:
            adobe = self.soup.find(class_="activity adobeconnect modtype_adobeconnect").find('a')['href']
            response = self.session.get(adobe)
            self.soup = BeautifulSoup(response.text, 'html.parser')
            class_time = self.soup.find(class_="aconmeetinforow").find_all(class_="aconlabeltitle")[-1].text
            d_c = class_time.split('از ساعت')
            days = d_c[0].split('زمان تشکیل جلسه :هر')[-1].split(' و ')
            days_list = []
            for day in days:
                day = day.strip(' ')
                days_list.append(day)
            clock = d_c[-1].split(' ')[1]
            return days_list, clock, True
        else:
            return None, None, False

    def get_course_teacher_id(self, course_info_link):
        try:
            response = self.session.get(course_info_link)
            soup = BeautifulSoup(response.text, 'html.parser')
            teacher = soup.find(class_="teachers").find('a')
            teacher_lms_id = teacher['href'].split('id=')[-1].split('&')[0]
            return teacher_lms_id
        except:
            return None

    def get_course_info(self, course_tag) -> (str, dict):
        course_id = course_tag['href'].split("&course=")[1].split("&")[0]
        course_name = course_tag.text
        course_term = course_name.split(" ")[-1]
        course_term = course_term[1:len(course_term) - 1]
        course_view_link = self.BASE_COURSE_VIEW_LINK + course_id
        course_info_link = self.BASE_COURSE_INFO_LINK + course_id
        return course_name, {"id": course_id, "term": course_term,
                             "view_link": course_view_link, "info_link": course_info_link}

    def close_session(self):
        self.session.close()
