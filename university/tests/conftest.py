import random

from accounts.models import User
from django.urls import reverse
from model_bakery import baker
from rest_framework.test import APIClient
import pytest

from university.models import Semester, BaseCourse, Teacher, Course, Department, AllowedDepartment
from utils.variables import project_variables
from utils.variables.project_variables import DOMAIN


# URLs:

@pytest.fixture
def api_client():
    return APIClient()


@pytest.fixture
def sign_up_department_list_view_url():
    return reverse('department-names')


@pytest.fixture
def departments_list_view_url():
    return reverse('departments')


@pytest.fixture
def sorted_department_list_view_url():
    return reverse('sorted-department-names')


@pytest.fixture
def semesters_list_view_url():
    return reverse('semesters')


@pytest.fixture
def course_timeline_view_url():
    def do_course_timeline_view_url(course_number):
        return reverse('course-timeline', kwargs={'course_number': course_number})

    return do_course_timeline_view_url


@pytest.fixture
def teacher_timeline_view_url():
    def do_teacher_timeline_view_url(teacher_pk):
        return reverse('teacher-timeline', kwargs={'teacher_pk': teacher_pk})

    return do_teacher_timeline_view_url


@pytest.fixture
def user_instance():
    return baker.make(User)


@pytest.fixture
def current_semester():
    return baker.make(Semester, year=project_variables.CURRENT_SEMESTER)


@pytest.fixture
def base_course_instance():
    return baker.make(BaseCourse, course_number='1234567')


@pytest.fixture
def course_instance(base_course_instance, current_semester):
    return baker.make(Course, base_course=base_course_instance, semester=current_semester, class_gp='01')


@pytest.fixture
def department_instance():
    return baker.make(Department, name='Computer Engineering', department_number=12)


@pytest.fixture
def allowed_department_instance(course_instance, department_instance):
    return baker.make(AllowedDepartment, course=course_instance, department=department_instance)


@pytest.fixture
def teachers():
    return baker.make(Teacher, _quantity=5)


@pytest.fixture
def base_courses():
    base_courses_list = []
    for i in range(1, 6):
        base_courses_list.append(baker.make(BaseCourse, course_number=1211011 + i))
    return base_courses_list


@pytest.fixture
def courses(base_courses, teachers, current_semester):
    courses_list = []
    for i in range(5):
        for j in range(1, 5):
            course = baker.make(Course,
                                base_course=base_courses[i], class_gp=f'0{j}',
                                semester=current_semester,
                                capacity=random.randint(1, 100),
                                registered_count=random.randint(1, 100),
                                waiting_count=random.randint(1, 100), )
            course.teachers.add(*teachers[i:j+1])
            courses_list.append(course)
    return courses_list


@pytest.fixture
def authenticate(api_client):
    def do_authenticate(is_staff=False):
        return api_client.force_authenticate(user=User(is_staff=is_staff, department=22))

    return do_authenticate
