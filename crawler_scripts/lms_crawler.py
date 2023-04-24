import os

from requests import Response
from crawler_scripts.bs4_crawler import BS4Crawler
from utils.image_handler import ImageHandler


class LMSCrawler(BS4Crawler):
    LOGIN_URL = 'https://lms.iust.ac.ir/login/index.php'
    AUTHENTICATION_URL = 'https://its.iust.ac.ir/oauth2/autheticate'
    BASE_COURSE_VIEW_LINK = 'https://lms.iust.ac.ir/course/view.php?id='
    BASE_COURSE_INFO_LINK = 'https://lms.iust.ac.ir/course/info.php?id='
    LMS_PROFILE_URL = 'https://lms.iust.ac.ir/user/profile.php'
    LMS_PROFILE_COUNT = 3260

    def __init__(self):
        super().__init__()
        self.image_handler = ImageHandler(os.path.abspath(os.path.join(__file__, os.pardir)) + '/teacher_images/')

    @staticmethod
    def get_login_data(username, password) -> dict:
        return {
            'name': username,
            "pass": password,
            "form_id": "oauth2_server_authenticate_form",
        }

    def login(self, username, password) -> Response | None:
        self.set_soup(self.LOGIN_URL)
        url = self.soup.find(class_="btn btn-primary btn-block")['href']
        self.session.get(url)
        data = self.get_login_data(username, password)
        response = self.session.post(self.AUTHENTICATION_URL, data=data)
        if response.status_code == 200:
            return response
        else:
            return None

    def find_user_courses(self, all_terms=False) -> dict:
        """
        Using this method we can get data about user's courses. this data can be from this term's courses or
        previous terms' courses.
        fields of data: {"id": course_lms_id, "term": course_term,
                        "view_link": course_view_link, "info_link": course_info_link,
                        "is_active": course_is_active, "days": days_list, "clock": course_clock_time,
                        "course_number", "course_group", "teacher_lms_id"}
        """
        self.set_soup(self.LMS_PROFILE_URL)
        courses_dict = {}
        courses = self.soup.find('li', class_="contentnode courseprofiles").find_all('a')
        if all_terms:
            self.set_soup(courses[-1]['href'])
            courses = self.soup.find('li', class_="contentnode courseprofiles").find_all('a')
        else:
            courses = [course for course in courses if course.span]

        for course in courses:
            course_name, course_info = self.get_course_info(course)
            days_list, clock, is_active, course_number, course_group = self.get_course_view_url_data(
                course_info['view_link'])
            course_info['days'] = days_list
            course_info['clock'] = clock
            course_info['is_active'] = is_active
            course_info['course_number'] = course_number
            course_info['course_group'] = course_group
            teacher_lms_id = self.get_course_teacher_id(course_info['info_link'])
            course_info['teacher_lms_id'] = teacher_lms_id
            courses_dict[course_name] = course_info

        return courses_dict

    def get_course_view_url_data(self, view_link):
        self.set_soup(view_link)
        try:
            adobe = self.soup.find(class_="activity adobeconnect modtype_adobeconnect").find('a')['href']
            is_active = True
        except AttributeError:
            try:
                adobe = self.soup.find(class_="activity adobearchive modtype_adobearchive").find('a')['href']
                is_active = False
            except:
                return None, None, False, None, None
        self.set_soup(adobe)
        days_list, clock = self.get_date_time_for_course(is_active)
        course_number, course_group = self.get_course_number_group()
        return days_list, clock, is_active, course_number, course_group

    def get_date_time_for_course(self, is_active) -> (str, str):
        if is_active:
            class_time = self.soup.find(class_="aconmeetinforow").find_all(class_="aconlabeltitle")[-1].text
            d_c = class_time.split('از ساعت')
            days = d_c[0].split('زمان تشکیل جلسه :هر')[-1].split(' و ')
            days_list = []
            for day in days:
                day = day.strip(' ')
                days_list.append(day)
            clock = d_c[-1].split(' ')[1]
            return days_list, clock
        else:
            return None, None

    def get_course_number_group(self):
        title = self.soup.find('title').string[-15:-1]
        title_parts = title.split('-')
        course_number = title_parts[1]
        course_group = title_parts[2]
        return course_number, course_group

    def get_course_teacher_id(self, course_info_link) -> str | None:
        try:
            self.set_soup(course_info_link)
            teacher = self.soup.find(class_="teachers").find('a')
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

    def get_teachers_info(self, start, count):
        data = []
        for i in range(start, start + count):
            teacher_info = self.get_teacher_info(i)
            if teacher_info is not None:
                data.append(teacher_info)
        return data

    def get_teacher_info(self, lms_id):
        self.set_soup(self.LMS_PROFILE_URL + '?id=' + str(lms_id))
        name = self.get_teacher_name()
        if name is None:
            return None
        email = self.get_teacher_email()
        img_url = self.get_teacher_image()
        return [name, email, img_url, lms_id]

    def get_teacher_name(self):
        try:
            return self.soup.find(class_="contentnode fullname").find('span').text
        except AttributeError:
            return None

    def get_teacher_email(self):
        try:
            return self.soup.find(class_="contentnode email").find('dd').text
        except AttributeError:
            return None

    def get_teacher_image(self):
        try:
            return self.soup.find(class_="contentnode userimage adaptableuserpicture").find('img').get('src')
        except AttributeError:
            return None
