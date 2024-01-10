import random

from accounts.models import User
from django.urls import reverse
from model_bakery import baker
from rest_framework.test import APIClient
import pytest

from university.models import Semester, BaseCourse, Teacher, Course, Department, AllowedDepartment, CourseTimePlace, \
    ExamTimePlace
from utils.variables import project_variables


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
    return baker.make(User, gender='M')


@pytest.fixture
def user_with_department(departments):
    return baker.make(User, department=departments[0], gender='M')


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
def courses(base_courses, teachers, current_semester, departments):
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
            course.teachers.add(*teachers[i:j + 1])
            courses_list.append(course)
    return courses_list


@pytest.fixture
def courses_in_first_department(courses, departments, user_instance):
    return [course for course in courses if
            course.base_course.department == departments[0] and (
                    course.sex == user_instance.gender or course.sex == 'B')]


@pytest.fixture
def courses_with_user_department(courses, departments, user_with_department):
    return [course for course in courses if
            course.base_course.department.department_number == user_with_department.department.department_number and (
                    course.sex == user_with_department.gender or course.sex == 'B')]


@pytest.fixture
def authenticate(api_client):
    def do_authenticate(is_staff=False):
        return api_client.force_authenticate(user=User(is_staff=is_staff, department=22))

    return do_authenticate
