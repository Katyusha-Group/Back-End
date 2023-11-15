import itertools

import pytest
from rest_framework import status
from model_bakery import baker

from university.models import Course
from utils.variables import project_variables


@pytest.mark.django_db
class TestCourseTimeLine:
    def test_if_get_request_is_status_200_for_login_user(self, api_client, user_instance, current_semester,
                                                         base_courses, course_timeline_view_url):
        course = baker.make(Course, base_course=base_courses[0], class_gp='01', semester=current_semester)
        api_client.force_login(user_instance)

        response = api_client.get(course_timeline_view_url(course.base_course_id))

        assert response.status_code == status.HTTP_200_OK

    def test_if_get_request_is_status_403_for_unauthenticated_user(self, api_client, current_semester, base_courses,
                                                                   course_timeline_view_url):
        course = baker.make(Course, base_course=base_courses[0], class_gp='01', semester=current_semester)

        response = api_client.get(course_timeline_view_url(course.base_course_id))

        assert response.status_code == status.HTTP_403_FORBIDDEN

    def test_if_put_request_is_status_405(self, api_client, user_instance, current_semester,
                                          base_courses, course_timeline_view_url):
        course = baker.make(Course, base_course=base_courses[0], class_gp='01', semester=current_semester)
        api_client.force_login(user_instance)

        response = api_client.put(course_timeline_view_url(course.base_course_id))

        assert response.status_code == status.HTTP_405_METHOD_NOT_ALLOWED

    def test_if_post_request_is_status_405(self, api_client, user_instance, current_semester,
                                           base_courses, course_timeline_view_url):
        course = baker.make(Course, base_course=base_courses[0], class_gp='01', semester=current_semester)
        api_client.force_login(user_instance)

        response = api_client.post(course_timeline_view_url(course.base_course_id))

        assert response.status_code == status.HTTP_405_METHOD_NOT_ALLOWED

    def test_if_delete_request_is_status_405(self, api_client, user_instance, current_semester,
                                             base_courses, course_timeline_view_url):
        course = baker.make(Course, base_course=base_courses[0], class_gp='01', semester=current_semester)
        api_client.force_login(user_instance)

        response = api_client.delete(course_timeline_view_url(course.base_course_id))

        assert response.status_code == status.HTTP_405_METHOD_NOT_ALLOWED

    def test_if_patch_request_is_status_405(self, api_client, user_instance, current_semester,
                                            base_courses, course_timeline_view_url):
        course = baker.make(Course, base_course=base_courses[0], class_gp='01', semester=current_semester)
        api_client.force_login(user_instance)

        response = api_client.patch(course_timeline_view_url(course.base_course_id))

        assert response.status_code == status.HTTP_405_METHOD_NOT_ALLOWED

    def test_if_get_request_has_correct_keys(self, api_client, user_instance,
                                             courses, course_timeline_view_url):
        first_teacher_name = courses[0].teachers.all()[0].name
        api_client.force_login(user_instance)

        response = api_client.get(course_timeline_view_url(courses[0].base_course_id))
        assert response.data[0].keys() == {'course_number', 'name', 'data'}
        assert response.data[0]['data'].keys().__contains__(project_variables.CURRENT_SEMESTER)
        assert response.data[0]['data'][project_variables.CURRENT_SEMESTER].keys().__contains__(first_teacher_name)
        assert response.data[0]['data'][project_variables.CURRENT_SEMESTER][first_teacher_name].keys() == {'courses',
                                                                                                           'total_capacity',
                                                                                                           'total_registered_count',
                                                                                                           'popularity',
                                                                                                           'total_classes'}
        assert \
            response.data[0]['data'][project_variables.CURRENT_SEMESTER][first_teacher_name]['courses'][0].keys() == {
                'capacity', 'registered_count', 'complete_course_number'}

    def test_if_get_request_has_correct_values(self, api_client, user_instance,
                                               courses, course_timeline_view_url):
        api_client.force_login(user_instance)
        first_teacher_name = courses[0].teachers.all()[0].name

        response = api_client.get(course_timeline_view_url(courses[0].base_course_id))

        assert response.data[0]['course_number'] == courses[0].base_course.course_number
        assert response.data[0]['name'] == courses[0].base_course.name
        assert response.data[0]['data'][project_variables.CURRENT_SEMESTER][first_teacher_name]['courses'][0][
                   'capacity'] == courses[0].capacity
        assert response.data[0]['data'][project_variables.CURRENT_SEMESTER][first_teacher_name]['courses'][0][
                   'registered_count'] == courses[0].registered_count

    def test_if_get_request_has_correct_values_for_multiple_teachers(self, api_client, user_instance,
                                                                     courses, course_timeline_view_url):
        api_client.force_login(user_instance)

        response = api_client.get(course_timeline_view_url(courses[0].base_course_id))

        for teacher in courses[0].teachers.all():
            course = response.data[0]['data'][project_variables.CURRENT_SEMESTER][teacher.name]['courses'][0]
            assert course['capacity'] == courses[0].capacity
            assert course['registered_count'] == courses[0].registered_count
            assert course['capacity'] == courses[0].capacity

    def test_if_get_request_has_correct_length_of_teachers_for_multiple_teachers(self, api_client, user_instance,
                                                                                 courses, course_timeline_view_url):
        api_client.force_login(user_instance)

        response = api_client.get(course_timeline_view_url(courses[0].base_course_id))

        course_teachers = [course.teachers.all() for course in courses[0].base_course.courses.all()]
        course_teachers = list(itertools.chain(*course_teachers))
        course_teachers = list(set(course_teachers))
        assert len(response.data[0]['data'][project_variables.CURRENT_SEMESTER].keys()) == len(course_teachers)

    def test_if_total_capacity_is_correct(self, api_client, user_instance,
                                          courses, course_timeline_view_url):
        api_client.force_login(user_instance)

        response = api_client.get(course_timeline_view_url(courses[0].base_course_id))

        current_semester_data = response.data[0]['data'][project_variables.CURRENT_SEMESTER]
        for teacher in current_semester_data.keys():
            total_capacity = 0
            for course in current_semester_data[teacher]['courses']:
                total_capacity += course['capacity']
            assert total_capacity == current_semester_data[teacher]['total_capacity']

    def test_if_total_registered_count_is_correct(self, api_client, user_instance,
                                                  courses, course_timeline_view_url):
        api_client.force_login(user_instance)

        response = api_client.get(course_timeline_view_url(courses[0].base_course_id))

        current_semester_data = response.data[0]['data'][project_variables.CURRENT_SEMESTER]
        for teacher in current_semester_data.keys():
            total_registered_count = 0
            for course in current_semester_data[teacher]['courses']:
                total_registered_count += course['registered_count']
            assert total_registered_count == current_semester_data[teacher]['total_registered_count']


@pytest.mark.django_db
class TestTeacherTimeLine:
    def test_if_get_request_is_status_200(self, api_client, user_instance, teachers, teacher_timeline_view_url):
        api_client.force_login(user_instance)

        response = api_client.get(teacher_timeline_view_url(teachers[0].id))

        assert response.status_code == status.HTTP_200_OK

    def test_if_get_request_is_status_403_for_unauthenticated_user(self, api_client, teachers,
                                                                   teacher_timeline_view_url):
        response = api_client.get(teacher_timeline_view_url(teachers[0].id))

        assert response.status_code == status.HTTP_403_FORBIDDEN

    def test_if_put_request_is_status_405(self, api_client, user_instance, teachers, teacher_timeline_view_url):
        api_client.force_login(user_instance)

        response = api_client.put(teacher_timeline_view_url(teachers[0].id))

        assert response.status_code == status.HTTP_405_METHOD_NOT_ALLOWED

    def test_if_post_request_is_status_405(self, api_client, user_instance, teachers, teacher_timeline_view_url):
        api_client.force_login(user_instance)

        response = api_client.post(teacher_timeline_view_url(teachers[0].id))

        assert response.status_code == status.HTTP_405_METHOD_NOT_ALLOWED

    def test_if_delete_request_is_status_405(self, api_client, user_instance, teachers, teacher_timeline_view_url):
        api_client.force_login(user_instance)

        response = api_client.delete(teacher_timeline_view_url(teachers[0].id))

        assert response.status_code == status.HTTP_405_METHOD_NOT_ALLOWED

    def test_if_patch_request_is_status_405(self, api_client, user_instance, teachers, teacher_timeline_view_url):
        api_client.force_login(user_instance)

        response = api_client.patch(teacher_timeline_view_url(teachers[0].id))

        assert response.status_code == status.HTTP_405_METHOD_NOT_ALLOWED

    def test_if_get_request_has_correct_keys(self, api_client, user_instance, teachers, courses,
                                             teacher_timeline_view_url):
        api_client.force_login(user_instance)
        first_teacher_course_names = [course.base_course.name for course in teachers[0].courses.all()]

        response = api_client.get(teacher_timeline_view_url(teachers[0].id))

        assert response.data[0].keys() == {'name', 'data'}
        assert response.data[0]['data'].keys().__contains__(project_variables.CURRENT_SEMESTER)
        assert response.data[0]['data'][project_variables.CURRENT_SEMESTER].keys().__contains__(
            'courses')
        assert response.data[0]['data'][project_variables.CURRENT_SEMESTER]['courses'].keys().__contains__(
            first_teacher_course_names[0])
        assert response.data[0]['data'][project_variables.CURRENT_SEMESTER]['courses'][
                   first_teacher_course_names[0]].keys() == {
                   'detail', 'course_total_capacity', 'course_total_registered_count', 'course_popularity',
                   'course_total_classes'}
        assert response.data[0]['data'][project_variables.CURRENT_SEMESTER]['courses'][first_teacher_course_names[0]][
                   'detail'][0].keys() == {'capacity', 'registered_count'}

    def test_if_get_request_has_correct_values_single_course_check(self, api_client, user_instance, teachers, courses,
                                                                   teacher_timeline_view_url):
        api_client.force_login(user_instance)
        first_teacher_course_name = teachers[0].courses.all()[0].base_course.name

        response = api_client.get(teacher_timeline_view_url(teachers[0].id))

        assert response.data[0]['data'][project_variables.CURRENT_SEMESTER]['courses'][first_teacher_course_name][
                   'detail'][0]['capacity'] == courses[0].capacity
        assert response.data[0]['data'][project_variables.CURRENT_SEMESTER]['courses'][first_teacher_course_name][
                   'detail'][0]['registered_count'] == courses[0].registered_count

    def test_if_get_request_has_correct_values_for_multiple_courses(self, api_client, user_instance, teachers, courses,
                                                                    teacher_timeline_view_url):
        first_teacher_course = [course for course in teachers[0].courses.all()]
        api_client.force_login(user_instance)

        response = api_client.get(teacher_timeline_view_url(teachers[0].id))

        response_courses = response.data[0]['data'][project_variables.CURRENT_SEMESTER]['courses'].keys()

        for course, response_course in zip(first_teacher_course, response_courses):
            assert response.data[0]['data'][project_variables.CURRENT_SEMESTER]['courses'][response_course][
                       'detail'][0]['capacity'] == course.capacity
            assert response.data[0]['data'][project_variables.CURRENT_SEMESTER]['courses'][response_course][
                       'detail'][0]['registered_count'] == course.registered_count

    def test_if_get_request_has_correct_counts_for_multiple_courses(self, api_client, user_instance, teachers, courses,
                                                                    teacher_timeline_view_url):
        first_teacher_course = [course for course in teachers[0].courses.all()]
        api_client.force_login(user_instance)
        total = 0

        response = api_client.get(teacher_timeline_view_url(teachers[0].id))

        for course in response.data[0]['data'][project_variables.CURRENT_SEMESTER]['courses']:
            total += len(response.data[0]['data'][project_variables.CURRENT_SEMESTER]['courses'][course]['detail'])

        assert total == len(first_teacher_course)

    def test_if_total_capacity_is_correct(self, api_client, user_instance, teachers, courses,
                                          teacher_timeline_view_url):
        api_client.force_login(user_instance)

        response = api_client.get(teacher_timeline_view_url(teachers[0].id))

        current_semester_data = response.data[0]['data'][project_variables.CURRENT_SEMESTER]['courses']
        for course in current_semester_data.keys():
            total_capacity = 0
            for d in current_semester_data[course]['detail']:
                total_capacity += d['capacity']
            assert total_capacity == current_semester_data[course]['course_total_capacity']

    def test_if_total_registered_count_is_correct(self, api_client, user_instance, teachers, courses,
                                                  teacher_timeline_view_url):
        api_client.force_login(user_instance)

        response = api_client.get(teacher_timeline_view_url(teachers[0].id))

        current_semester_data = response.data[0]['data'][project_variables.CURRENT_SEMESTER]['courses']
        for course in current_semester_data.keys():
            total_registered_count = 0
            for d in current_semester_data[course]['detail']:
                total_registered_count += d['registered_count']
            assert total_registered_count == current_semester_data[course]['course_total_registered_count']
