import pytest
from django.urls import reverse
from rest_framework import status
from model_bakery import baker

from university.models import Department
from utils.variables import project_variables

pytestmark = pytest.mark.django_db


@pytest.fixture
def all_department_based_courses_view_url():
    def do(department_number):
        return reverse('all-course-department_retrieve', kwargs={'department_number': department_number})

    return do


class TestCoursesBasedDepartments:
    def test_if_get_request_is_status_200(self, user_instance, api_client, all_department_based_courses_view_url,
                                          courses, departments):
        api_client.force_login(user_instance)
        response = api_client.get(all_department_based_courses_view_url(departments[0].department_number))
        assert response.status_code == status.HTTP_200_OK

    def test_if_get_request_for_not_found_department_is_status_404(self, user_instance, api_client,
                                                                   all_department_based_courses_view_url,
                                                                   departments):
        api_client.force_login(user_instance)
        response = api_client.get(all_department_based_courses_view_url(100))
        assert response.status_code == status.HTTP_404_NOT_FOUND

    def test_if_get_request_is_status_403_for_anonymous_user(self, user_instance, api_client,
                                                             all_department_based_courses_view_url,
                                                             departments):
        response = api_client.get(all_department_based_courses_view_url(departments[0].department_number))
        assert response.status_code == status.HTTP_403_FORBIDDEN

    def test_if_get_request_is_status_404_if_department_has_any_course(self, user_instance, api_client,
                                                                       all_department_based_courses_view_url,
                                                                       departments, courses):
        department = baker.make(Department)
        api_client.force_login(user_instance)
        response = api_client.get(all_department_based_courses_view_url(department.department_number))
        assert response.status_code == status.HTTP_404_NOT_FOUND

    def test_if_post_request_is_status_405(self, user_instance, api_client, all_department_based_courses_view_url,
                                           departments):
        api_client.force_login(user_instance)
        response = api_client.post(all_department_based_courses_view_url(departments[0].department_number))
        assert response.status_code == status.HTTP_405_METHOD_NOT_ALLOWED

    def test_if_put_request_is_status_405(self, user_instance, api_client, all_department_based_courses_view_url,
                                          departments):
        api_client.force_login(user_instance)
        response = api_client.put(all_department_based_courses_view_url(departments[0].department_number))
        assert response.status_code == status.HTTP_405_METHOD_NOT_ALLOWED

    def test_if_patch_request_is_status_405(self, user_instance, api_client, all_department_based_courses_view_url,
                                            departments):
        api_client.force_login(user_instance)
        response = api_client.patch(all_department_based_courses_view_url(departments[0].department_number))
        assert response.status_code == status.HTTP_405_METHOD_NOT_ALLOWED

    def test_if_delete_request_is_status_405(self, user_instance, api_client, all_department_based_courses_view_url,
                                             departments):
        api_client.force_login(user_instance)
        response = api_client.delete(all_department_based_courses_view_url(departments[0].department_number))
        assert response.status_code == status.HTTP_405_METHOD_NOT_ALLOWED

    def test_if_returned_data_only_contains_courses_with_defined_department(self, user_instance, api_client,
                                                                            all_department_based_courses_view_url,
                                                                            departments, courses,
                                                                            courses_in_first_department):
        api_client.force_login(user_instance)
        response = api_client.get(all_department_based_courses_view_url(departments[0].department_number))
        assert len(response.data) == len(courses_in_first_department)

    def test_if_returned_data_contains_all_courses_with_defined_department(self, user_instance, api_client,
                                                                           all_department_based_courses_view_url,
                                                                           departments, courses,
                                                                           courses_in_first_department):
        api_client.force_login(user_instance)
        response = api_client.get(all_department_based_courses_view_url(departments[0].department_number))
        for course in courses_in_first_department:
            assert course.complete_course_number in [course['complete_course_number'] for course in response.data]

    def test_if_returned_data_has_correct_length_of_keys(self, api_client, user_instance, departments,
                                                         all_department_based_courses_view_url, courses):
        api_client.force_login(user_instance)
        response = api_client.get(
            all_department_based_courses_view_url(departments[0].department_number))
        assert len(response.data[0].keys()) == 19

    def test_if_returned_data_has_correct_keys(self, api_client, user_instance, departments,
                                               all_department_based_courses_view_url, courses):
        api_client.force_login(user_instance)
        response = api_client.get(
            all_department_based_courses_view_url(departments[0].department_number))
        assert set(response.data[0].keys()) == {
            'id', 'name', 'is_allowed', 'class_gp', 'capacity',
            'complete_course_number', 'registered_count', 'waiting_count',
            'guest_able', 'course_times', 'color_intensity_percentage',
            'registration_limit', 'description', 'sex', 'presentation_type',
            'base_course', 'teachers', 'exam_times', 'allowed_departments'
        }

    def test_if_returned_data_has_correct_values(self, api_client, departments, user_instance,
                                                 all_department_based_courses_view_url,
                                                 courses_in_first_department):
        api_client.force_login(user=user_instance)

        response = api_client.get(all_department_based_courses_view_url(departments[0].department_number))

        assert response.data[0]['id'] == courses_in_first_department[0].id
        assert response.data[0]['name'] == courses_in_first_department[0].base_course.name
        assert response.data[0]['class_gp'] == courses_in_first_department[0].class_gp
        assert response.data[0]['capacity'] == courses_in_first_department[0].capacity
        assert response.data[0]['registered_count'] == courses_in_first_department[0].registered_count
        assert response.data[0]['waiting_count'] == courses_in_first_department[0].waiting_count
        assert response.data[0]['guest_able'] == courses_in_first_department[0].guest_able
        assert response.data[0]['registration_limit'] == courses_in_first_department[0].registration_limit
        assert response.data[0]['description'] == courses_in_first_department[0].description
        assert response.data[0]['base_course'] == courses_in_first_department[0].base_course.course_number

    def test_if_returned_data_has_correct_keys_in_course_times(self, api_client, departments, user_instance,
                                                               all_department_based_courses_view_url,
                                                               courses_in_first_department):
        api_client.force_login(user=user_instance)

        response = api_client.get(all_department_based_courses_view_url(departments[0].department_number))

        assert set(response.data[0]['course_times'][0].keys()) == {
            'course_day', 'course_start_time', 'course_end_time', 'place', 'course_time_representation'
        }

    def test_if_returned_data_has_correct_keys_in_exam_times(self, api_client, user_instance, departments,
                                                             all_department_based_courses_view_url, courses):
        api_client.force_login(user=user_instance)

        response = api_client.get(all_department_based_courses_view_url(departments[0].department_number))

        assert response.data[0]['exam_times'][0].keys() == {
            'date', 'exam_start_time', 'exam_end_time'
        }

    def test_if_returned_data_has_correct_keys_in_teachers(self, api_client, user_instance, departments,
                                                           all_department_based_courses_view_url, courses):
        api_client.force_login(user=user_instance)

        response = api_client.get(all_department_based_courses_view_url(departments[0].department_number))

        assert response.data[0]['teachers'][0].keys() == {
            'id', 'name', 'teacher_image'
        }

    def test_if_returned_data_has_correct_values_in_course_times_list(self, api_client, user_instance, departments,
                                                                      all_department_based_courses_view_url,
                                                                      courses_in_first_department):
        api_client.force_login(user=user_instance)

        response = api_client.get(all_department_based_courses_view_url(departments[0].department_number))

        course_time = courses_in_first_department[0].course_times.all()
        response_course_time = response.data[0]['course_times']
        assert len(response_course_time) == len(course_time)
        for i in range(len(response_course_time)):
            start = int((str(course_time[i].start_time))[:2])
            if start in project_variables.start_time_mapper:
                course_time_presentation = project_variables.start_time_mapper[start]
            else:
                course_time_presentation = 7

            assert str(response_course_time[i]['course_day']) == str(course_time[i].day)
            assert str(response_course_time[i]['course_start_time']).split('.')[0] == \
                   str(course_time[i].start_time).split('.')[0]
            assert str(response_course_time[i]['course_end_time']).split('.')[0] == \
                   str(course_time[i].end_time).split('.')[0]
            assert str(response_course_time[i]['place']) == str(course_time[i].place)
            assert str(response_course_time[i]['course_time_representation']) == str(course_time_presentation)

    def test_if_returned_data_has_correct_values_in_exam_times_list(self, api_client, user_instance, departments,
                                                                    all_department_based_courses_view_url,
                                                                    courses_in_first_department):
        api_client.force_login(user=user_instance)

        response = api_client.get(all_department_based_courses_view_url(departments[0].department_number))

        exam_time = courses_in_first_department[0].exam_times.all()
        response_exam_time = response.data[0]['exam_times']
        assert len(response_exam_time) == len(exam_time)
        for i in range(len(response_exam_time)):
            assert str(response_exam_time[i]['date']).split('.')[0] == str(exam_time[i].date).split('.')[0]
            assert str(response_exam_time[i]['exam_start_time']).split('.')[0] == \
                   str(exam_time[i].start_time).split('.')[0]
            assert str(response_exam_time[i]['exam_end_time']) == str(exam_time[i].end_time)

    def test_if_returned_data_has_correct_values_in_teachers_list(self, api_client, user_instance, departments,
                                                                  all_department_based_courses_view_url,
                                                                  courses_in_first_department):
        api_client.force_login(user=user_instance)

        response = api_client.get(all_department_based_courses_view_url(departments[0].department_number))

        teachers = courses_in_first_department[0].teachers.all()
        response_teachers = response.data[0]['teachers']
        assert len(response_teachers) == len(teachers)
        for i in range(len(response_teachers)):
            assert str(response_teachers[i]['id']) == str(teachers[i].id)
            assert str(response_teachers[i]['name']) == str(teachers[i].name)
            assert str(response_teachers[i]['teacher_image']) == str(teachers[i].image_full_path)

    @pytest.mark.skip
    def test_if_returned_data_has_correct_complete_course_number(self, api_client, user_instance, departments,
                                                                 all_department_based_courses_view_url,
                                                                 courses_in_first_department):
        api_client.force_login(user=user_instance)

        response = api_client.get(all_department_based_courses_view_url(departments[0].department_number))

        for i in range(len(response.data)):
            if response.data[i]['complete_course_number'] == courses_in_first_department[i].complete_course_number:
                assert True
        assert False

    @pytest.mark.skip
    def test_if_returned_data_has_correct_color_intensity(self, api_client, user_instance, departments,
                                                          all_department_based_courses_view_url,
                                                          courses_in_first_department):
        api_client.force_login(user=user_instance)

        response = api_client.get(all_department_based_courses_view_url(departments[0].department_number))

        for i in range(len(response.data)):
            if response.data[i]['color_intensity_percentage'] == courses_in_first_department[
                i].color_intensity_percentage:
                assert True
        assert False

    @pytest.mark.skip
    def test_if_returned_data_has_correct_is_allowed_field(self, api_client, user_instance, departments,
                                                           all_department_based_courses_view_url,
                                                           courses_in_first_department):
        api_client.force_login(user=user_instance)
        is_first_allowed = courses_in_first_department[0].allowed_departments.filter(
            department__department_number=user_instance.department.department_number).exists()

        response = api_client.get(all_department_based_courses_view_url(departments[0].department_number))

        for i in range(len(response.data)):
            if response.data[i]['is_allowed'] == is_first_allowed:
                assert True
        assert False
