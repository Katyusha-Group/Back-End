import random

from accounts.models import User
from django.urls import reverse
from model_bakery import baker
from rest_framework.test import APIClient
import pytest

from custom_config.models import Cart, Order
from university.models import Semester, Department, BaseCourse, Course, ExamTimePlace, CourseTimePlace, \
    AllowedDepartment
from utils.variables import project_variables


@pytest.fixture
def api_client():
    return APIClient()


@pytest.fixture
def user_instance():
    return baker.make(User, gender='M')


@pytest.fixture
def admin_user_instance():
    return baker.make(User, is_superuser=True, is_staff=True)


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
def cart_instance(user_instance):
    return baker.make(Cart, user=user_instance)

@pytest.fixture
def order_instance(user_instance):
    return baker.make(Order, user=user_instance)


@pytest.fixture
def departments():
    department_list = []
    for i in range(1, 6):
        department_list.append(baker.make(Department, department_number=i))
    return department_list


@pytest.fixture
def base_courses(departments):
    base_courses_list = []
    for i in range(1, 6):
        base_courses_list.append(baker.make(BaseCourse, course_number=1211011 + i, department=departments[i - 1]))
    return base_courses_list


@pytest.fixture
def courses(base_courses, current_semester, departments):
    courses_list = []
    for i in range(5):
        for j in range(1, 5):
            course = baker.make(Course,
                                base_course=base_courses[i],
                                class_gp=f'0{j}',
                                semester=current_semester,
                                capacity=random.randint(1, 100),
                                registered_count=random.randint(1, 100),
                                waiting_count=random.randint(1, 100),
                                sex=random.choice(['M', 'F', 'B']),
                                )
            baker.make(CourseTimePlace, course=course, _quantity=2)
            baker.make(ExamTimePlace, course=course, _quantity=1)
            department = random.choice(departments)
            if department != base_courses[i].department:
                baker.make(AllowedDepartment, course=course, department=department)
            baker.make(AllowedDepartment, course=course, department=base_courses[i].department)
            courses_list.append(course)
    return courses_list
