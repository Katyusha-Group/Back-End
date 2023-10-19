import pytest
from rest_framework import status
from model_bakery import baker

from university.models import Course, BaseCourse, Semester
from utils.variables import project_variables


@pytest.mark.django_db
class TestCourseTimeLine:
    def test_if_get_request_is_status_200_for_login_user(self, api_client, simple_user, current_semester,
                                                         base_courses, course_timeline_view_url):
        course = baker.make(Course, base_course=base_courses[0], class_gp='01', semester=current_semester)
        api_client.force_login(simple_user)

        response = api_client.get(course_timeline_view_url(course.base_course_id))

        assert response.status_code == status.HTTP_200_OK

    def test_if_get_request_is_status_403_for_unauthenticated_user(self, api_client, current_semester, base_courses,
                                                                   course_timeline_view_url):
        course = baker.make(Course, base_course=base_courses[0], class_gp='01', semester=current_semester)

        response = api_client.get(course_timeline_view_url(course.base_course_id))

        assert response.status_code == status.HTTP_403_FORBIDDEN

    def test_if_put_request_is_status_405(self, api_client, simple_user, current_semester,
                                          base_courses, course_timeline_view_url):
        course = baker.make(Course, base_course=base_courses[0], class_gp='01', semester=current_semester)
        api_client.force_login(simple_user)

        response = api_client.put(course_timeline_view_url(course.base_course_id))

        assert response.status_code == status.HTTP_405_METHOD_NOT_ALLOWED

    def test_if_post_request_is_status_405(self, api_client, simple_user, current_semester,
                                           base_courses, course_timeline_view_url):
        course = baker.make(Course, base_course=base_courses[0], class_gp='01', semester=current_semester)
        api_client.force_login(simple_user)

        response = api_client.post(course_timeline_view_url(course.base_course_id))

        assert response.status_code == status.HTTP_405_METHOD_NOT_ALLOWED

    def test_if_delete_request_is_status_405(self, api_client, simple_user, current_semester,
                                             base_courses, course_timeline_view_url):
        course = baker.make(Course, base_course=base_courses[0], class_gp='01', semester=current_semester)
        api_client.force_login(simple_user)

        response = api_client.delete(course_timeline_view_url(course.base_course_id))

        assert response.status_code == status.HTTP_405_METHOD_NOT_ALLOWED

    def test_if_patch_request_is_status_405(self, api_client, simple_user, current_semester,
                                            base_courses, course_timeline_view_url):
        course = baker.make(Course, base_course=base_courses[0], class_gp='01', semester=current_semester)
        api_client.force_login(simple_user)

        response = api_client.patch(course_timeline_view_url(course.base_course_id))

        assert response.status_code == status.HTTP_405_METHOD_NOT_ALLOWED

    def test_if_get_request_has_correct_keys(self, api_client, simple_user, current_semester,
                                             courses, course_timeline_view_url):
        first_teacher_name = courses[0].teachers.all()[0].name
        api_client.force_login(simple_user)

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

    def test_if_get_request_has_correct_values(self, api_client, simple_user, current_semester,
                                               courses, course_timeline_view_url):
        api_client.force_login(simple_user)
        first_teacher_name = courses[0].teachers.all()[0].name

        response = api_client.get(course_timeline_view_url(courses[0].base_course_id))

        assert response.data[0]['course_number'] == courses[0].base_course.course_number
        assert response.data[0]['name'] == courses[0].base_course.name
        assert response.data[0]['data'][project_variables.CURRENT_SEMESTER][first_teacher_name]['courses'][0][
                   'capacity'] == courses[0].capacity
        assert response.data[0]['data'][project_variables.CURRENT_SEMESTER][first_teacher_name]['courses'][0][
                   'registered_count'] == courses[0].registered_count

    def test_if_get_request_has_correct_values_for_multiple_teachers(self, api_client, simple_user, current_semester,
                                                                     courses, course_timeline_view_url):
        api_client.force_login(simple_user)

        response = api_client.get(course_timeline_view_url(courses[0].base_course_id))

        for teacher in courses[0].teachers.all():
            assert response.data[0]['data'][project_variables.CURRENT_SEMESTER][teacher.name]['courses'][0][
                       'capacity'] == courses[0].capacity
            assert response.data[0]['data'][project_variables.CURRENT_SEMESTER][teacher.name]['courses'][0][
                       'registered_count'] == courses[0].registered_count
            assert response.data[0]['data'][project_variables.CURRENT_SEMESTER][teacher.name]['courses'][0][
                       'capacity'] == \
                   courses[0].capacity
