import pytest
from django.urls import reverse
from rest_framework import status

from utils.variables import project_variables

pytestmark = pytest.mark.django_db


class TestMyCourses:
    @pytest.fixture
    def url(self):
        return reverse('courses-my-courses')

    @pytest.fixture
    def course(self, courses):
        return courses[0]

    def test_if_get_request_for_logged_in_user_is_status_200(self, api_client, user_instance, url):
        api_client.force_login(user_instance)
        response = api_client.get(url)

        assert response.status_code == status.HTTP_200_OK

    def test_if_get_request_for_anonymous_user_is_status_403(self, api_client, url):
        response = api_client.get(url)

        assert response.status_code == status.HTTP_403_FORBIDDEN

    def test_if_put_request_for_anonymous_user_is_status_403(self, api_client, url):
        response = api_client.put(url)

        assert response.status_code == status.HTTP_403_FORBIDDEN

    def test_if_post_request_is_status_405_for_logged_in(self, api_client, user_instance, url):
        api_client.force_login(user_instance)
        response = api_client.post(url)

        assert response.status_code == status.HTTP_405_METHOD_NOT_ALLOWED

    def test_if_delete_request_is_status_405_for_logged_in(self, api_client, user_instance, url):
        api_client.force_login(user_instance)
        response = api_client.delete(url)

        assert response.status_code == status.HTTP_405_METHOD_NOT_ALLOWED

    def test_if_patch_request_is_status_405_for_logged_in(self, api_client, user_instance, url):
        api_client.force_login(user_instance)
        response = api_client.patch(url)

    def test_if_post_request_is_status_403_for_anonymous(self, api_client, url):
        response = api_client.post(url)

        assert response.status_code == status.HTTP_403_FORBIDDEN

    def test_if_delete_request_is_status_403_for_anonymous(self, api_client, url):
        response = api_client.delete(url)

        assert response.status_code == status.HTTP_403_FORBIDDEN

    def test_if_patch_request_is_status_403_for_anonymous(self, api_client, url):
        response = api_client.patch(url)

        assert response.status_code == status.HTTP_403_FORBIDDEN

    def test_if_put_request_for_logged_in_user_adds_course_if_not_in_calendar(self, api_client, user_instance,
                                                                              url, course):
        api_client.force_login(user_instance)

        # Make a PUT request to add the course back to the user's calendar
        response = api_client.put(url, {'complete_course_number': course.complete_course_number})

        # Check if the course is added to the user's calendar
        user_instance.refresh_from_db()
        assert response.status_code == status.HTTP_200_OK
        assert course in user_instance.courses.all()

    def test_if_put_request_for_logged_in_user_removes_course_if_in_calendar(self, api_client, user_instance,
                                                                             url, course):
        api_client.force_login(user_instance)
        user_instance.courses.add(course)

        # Make a PUT request to remove the course from the user's calendar
        response = api_client.put(url, {'complete_course_number': course.complete_course_number})

        # Check if the course is removed from the user's calendar
        user_instance.refresh_from_db()
        assert response.status_code == status.HTTP_200_OK
        assert course not in user_instance.courses.all()

    def test_put_request_returns_404_for_non_existent_course(self, api_client, user_instance, url):
        api_client.force_login(user_instance)

        # Make a PUT request to add a course that does not exist
        response = api_client.put(url, {'complete_course_number': '1234567_01'})

        assert response.status_code == status.HTTP_404_NOT_FOUND

    def test_put_request_returns_400_for_invalid_course_number(self, api_client, user_instance, url):
        api_client.force_login(user_instance)

        response1 = api_client.put(url, {'complete_course_number': 'ab_ab'})
        response2 = api_client.put(url, {'complete_course_number': '1234567'})

        assert response1.status_code == status.HTTP_400_BAD_REQUEST
        assert response2.status_code == status.HTTP_400_BAD_REQUEST

    def test_get_request_returns_correct_number_of_fields(self, api_client, user_instance, url, course):
        api_client.force_login(user_instance)
        user_instance.courses.add(course)

        response = api_client.get(url)

        assert len(response.data[0]) == 18

    def test_get_request_returns_correct_fields(self, api_client, user_instance, url, course):
        api_client.force_login(user_instance)
        user_instance.courses.add(course)

        response = api_client.get(url)

        assert response.data[0].keys() == {'complete_course_number', 'name', 'group_number', 'total_unit',
                                           'practical_unit', 'capacity', 'registered_count',
                                           'waiting_count', 'sex', 'emergency_deletion',
                                           'registration_limit', 'description', 'presentation_type',
                                           'teachers', 'exam_times', 'course_times', 'is_allowed',
                                           'added_to_calendar_count'}

    def test_get_request_returns_correct_simple_data(self, api_client, user_instance, url, course):
        api_client.force_login(user_instance)
        user_instance.courses.add(course)

        response = api_client.get(url)

        assert response.data[0]['complete_course_number'] == course.complete_course_number, 'complete_course_number'
        assert response.data[0]['name'] == course.base_course.name, 'name'
        assert response.data[0]['group_number'] == course.class_gp, 'group_number'
        assert response.data[0]['total_unit'] == course.base_course.total_unit, 'total_unit'
        assert response.data[0]['practical_unit'] == course.base_course.practical_unit, 'practical_unit'
        assert response.data[0]['capacity'] == course.capacity, 'capacity'
        assert response.data[0]['registered_count'] == course.registered_count, 'registered_count'
        assert response.data[0]['waiting_count'] == course.waiting_count, 'waiting_count'
        assert response.data[0]['sex'] == course.sex, 'sex'
        assert response.data[0]['emergency_deletion'] == course.base_course.emergency_deletion, 'emergency_deletion'
        assert response.data[0]['registration_limit'] == course.registration_limit, 'registration_limit'
        assert response.data[0]['description'] == course.description, 'description'
        assert response.data[0]['presentation_type'] == course.presentation_type, 'presentation_type'

    def test_get_request_returns_correct_added_to_calendar_count_data(self, api_client, user_instance, url, course):
        api_client.force_login(user_instance)
        user_instance.courses.add(course)

        response = api_client.get(url)

        assert response.data[0]['added_to_calendar_count'] == 1

    def test_get_request_returns_correct_exam_times_data(self, api_client, user_instance, url, course):
        api_client.force_login(user_instance)
        user_instance.courses.add(course)
        first_exam_time = course.exam_times.first()

        response = api_client.get(url)

        assert response.data[0]['exam_times'][0].keys() == {'date', 'exam_start_time', 'exam_end_time'}

        assert str(response.data[0]['exam_times'][0]['date']).split('.')[0] == str(first_exam_time.date).split('.')[0], \
            'date'
        assert str(response.data[0]['exam_times'][0]['exam_start_time']).split('.')[0] == \
               str(first_exam_time.start_time).split('.')[0], 'start_time'
        assert str(response.data[0]['exam_times'][0]['exam_end_time']).split('.')[0] == \
               str(first_exam_time.end_time).split('.')[0], 'end_time'

    def test_get_request_returns_correct_course_times_data(self, api_client, user_instance, url, course):
        api_client.force_login(user_instance)
        user_instance.courses.add(course)
        first_course_time = course.course_times.first()
        start = int((str(first_course_time.start_time))[:2])
        if start in project_variables.start_time_mapper:
            course_time_representation = project_variables.start_time_mapper[start]
        else:
            course_time_representation = 7

        response = api_client.get(url)

        assert response.data[0]['course_times'][0].keys() == {'course_day', 'course_start_time', 'course_end_time',
                                                              'place', 'course_time_representation'}

        assert str(response.data[0]['course_times'][0]['course_day']) == str(first_course_time.day), 'day'
        assert str(response.data[0]['course_times'][0]['course_start_time']).split('.')[0] == \
               str(first_course_time.start_time).split('.')[0], 'start_time'
        assert str(response.data[0]['course_times'][0]['course_end_time']).split('.')[0] == \
               str(first_course_time.end_time).split('.')[0], 'end_time'
        assert response.data[0]['course_times'][0]['place'] == first_course_time.place, 'place'
        assert response.data[0]['course_times'][0][
                   'course_time_representation'] == course_time_representation, 'course_time_representation'

    def test_get_request_returns_correct_teachers_data(self, api_client, user_instance, url, course):
        api_client.force_login(user_instance)
        user_instance.courses.add(course)
        first_teacher = course.teachers.first()

        response = api_client.get(url)

        assert response.data[0]['teachers'][0].keys() == {'id', 'name', 'teacher_image'}

        assert response.data[0]['teachers'][0]['id'] == first_teacher.id, 'id'
        assert response.data[0]['teachers'][0]['name'] == first_teacher.name, 'name'
        assert response.data[0]['teachers'][0]['teacher_image'] == first_teacher.image_full_path, 'teacher_image'

    def test_get_request_returns_correct_is_allowed_data(self, api_client, user_instance, url, course):
        api_client.force_login(user_instance)
        user_instance.courses.add(course)
        is_allowed = course.allowed_departments.filter(
            department__department_number=user_instance.department.department_number).exists()

        response = api_client.get(url)

        assert response.data[0]['is_allowed'] == is_allowed
