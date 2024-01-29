import pytest
from django.urls import reverse
from rest_framework import status
from model_bakery import baker

from university.models import BaseCourse, Course, Semester
from utils.variables import project_variables

pytestmark = pytest.mark.django_db


class TestCoursegroups:
    @pytest.fixture
    def sorted_course_with_first_course_base_course_id(self, courses):
        courses_with_first_base_course_id = Course.objects.filter(base_course_id=courses[0].base_course_id,
                                                                  semester=project_variables.CURRENT_SEMESTER,
                                                                  sex__in=['B', 'M']).all()

        sorted_courses = sorted(courses_with_first_base_course_id, key=lambda x: (
            x.capacity - x.registered_count <= 0, x.capacity - x.registered_count, x.color_intensity_percentage))

        return sorted_courses

    @pytest.fixture
    def course_groups_view_url(self):
        def do_course_groups_view_url(base_course_pk):
            return reverse('course-groups', kwargs={'base_course_pk': base_course_pk})

        return do_course_groups_view_url

    def test_if_get_request_for_logged_in_user_is_status_200(self, api_client, user_instance, courses,
                                                             course_groups_view_url):
        api_client.force_login(user_instance)
        response = api_client.get(course_groups_view_url(courses[0].base_course_id))

        assert response.status_code == status.HTTP_200_OK

    def test_if_get_request_for_base_course_with_no_course_is_status_400(self, api_client, user_instance,
                                                                         course_groups_view_url):
        baker.make(BaseCourse, course_number=1)
        api_client.force_login(user_instance)
        response = api_client.get(course_groups_view_url(1))

        assert response.status_code == status.HTTP_400_BAD_REQUEST

    def test_if_get_request_for_nonexistent_base_course_is_status_400(self, api_client, user_instance,
                                                                      course_groups_view_url):
        api_client.force_login(user_instance)
        response = api_client.get(course_groups_view_url(1))

        assert response.status_code == status.HTTP_400_BAD_REQUEST

    def test_if_get_request_for_anonymous_user_is_status_403(self, api_client, user_instance, course_groups_view_url):
        baker.make(BaseCourse, course_number=1)
        response = api_client.get(course_groups_view_url(1))

        assert response.status_code == status.HTTP_403_FORBIDDEN

    def test_if_post_request_is_status_405(self, api_client, user_instance, course_groups_view_url):
        baker.make(BaseCourse, course_number=1)
        api_client.force_login(user_instance)
        response = api_client.post(course_groups_view_url(1))

        assert response.status_code == status.HTTP_405_METHOD_NOT_ALLOWED

    def test_if_put_request_is_status_405(self, api_client, user_instance, course_groups_view_url):
        baker.make(BaseCourse, course_number=1)
        api_client.force_login(user_instance)
        response = api_client.put(course_groups_view_url(1))

        assert response.status_code == status.HTTP_405_METHOD_NOT_ALLOWED

    def test_if_patch_request_is_status_405(self, api_client, user_instance, course_groups_view_url):
        baker.make(BaseCourse, course_number=1)
        api_client.force_login(user_instance)
        response = api_client.patch(course_groups_view_url(1))

        assert response.status_code == status.HTTP_405_METHOD_NOT_ALLOWED

    def test_if_delete_request_is_status_405(self, api_client, user_instance, course_groups_view_url):
        baker.make(BaseCourse, course_number=1)
        api_client.force_login(user_instance)
        response = api_client.delete(course_groups_view_url(1))

        assert response.status_code == status.HTTP_405_METHOD_NOT_ALLOWED

    def test_if_only_current_semester_courses_are_in_list(self, api_client, user_instance, course_groups_view_url):
        base_course = baker.make(BaseCourse, course_number=1)
        semester = baker.make(Semester, year=project_variables.CURRENT_SEMESTER)
        semester_old = baker.make(Semester, year=project_variables.CURRENT_SEMESTER - 1)
        baker.make(Course, base_course=base_course, semester=semester)
        baker.make(Course, base_course=base_course, semester=semester_old)

        api_client.force_login(user_instance)
        response = api_client.get(course_groups_view_url(base_course.course_number))

        assert len(response.data) == 1

    def test_if_returned_data_has_correct_number_of_fields(self, api_client, user_instance, course_groups_view_url,
                                                           courses):
        api_client.force_login(user_instance)

        response = api_client.get(course_groups_view_url(courses[0].base_course_id))

        assert len(response.data[0].keys()) == 17

    def test_if_returned_data_has_correct_fields(self, api_client, user_instance, course_groups_view_url, courses):
        api_client.force_login(user_instance)

        response = api_client.get(course_groups_view_url(courses[0].base_course_id))

        assert set(response.data[0].keys()) == {'complete_course_number', 'added_to_calendar_count', 'name',
                                                'base_course_id', 'group_number', 'capacity', 'registered_count',
                                                'waiting_count', 'exam_times', 'course_times', 'teachers',
                                                'color_intensity_percentage', 'total_unit', 'practical_unit', 'sex',
                                                'is_allowed', 'description'}

    def test_if_returned_data_is_sorted_correctly(self, api_client, user_instance, course_groups_view_url, courses,
                                                  sorted_course_with_first_course_base_course_id):
        api_client.force_login(user_instance)

        response = api_client.get(course_groups_view_url(courses[0].base_course_id))

        assert [course['complete_course_number'] for course in response.data] == (
            [course.complete_course_number for course in sorted_course_with_first_course_base_course_id])

    def test_if_returned_data_has_correct_values_for_simple_fields(self, api_client, user_instance,
                                                                   course_groups_view_url, courses,
                                                                   sorted_course_with_first_course_base_course_id):
        api_client.force_login(user_instance)

        response = api_client.get(course_groups_view_url(courses[0].base_course_id))

        for course_data, course in zip(response.data, sorted_course_with_first_course_base_course_id):
            assert course_data['base_course_id'] == course.base_course_id
            assert course_data['capacity'] == course.capacity
            assert course_data['color_intensity_percentage'] == course.color_intensity_percentage
            assert course_data['complete_course_number'] == course.complete_course_number
            assert course_data['description'] == course.description
            assert course_data['group_number'] == course.class_gp
            assert course_data['name'] == course.base_course.name
            assert course_data['practical_unit'] == course.base_course.practical_unit
            assert course_data['registered_count'] == course.registered_count
            assert course_data['sex'] == course.sex
            assert course_data['total_unit'] == course.base_course.total_unit
            assert course_data['waiting_count'] == course.waiting_count

    def test_if_returned_data_has_correct_values_for_course_times(self, api_client, user_instance,
                                                                  course_groups_view_url, courses,
                                                                  sorted_course_with_first_course_base_course_id):
        api_client.force_login(user_instance)

        response = api_client.get(course_groups_view_url(courses[0].base_course_id))

        for course_data, course in zip(response.data, sorted_course_with_first_course_base_course_id):
            for course_time_data, course_time in zip(course_data['course_times'], course.course_times.all()):
                start = int((str(course_time.start_time))[:2])
                if start in project_variables.start_time_mapper:
                    course_time_representation = project_variables.start_time_mapper[start]
                else:
                    course_time_representation = 7

                assert course_time_data['course_day'] == str(course_time.day)
                assert course_time_data['course_start_time'] == str(course_time.start_time)
                assert course_time_data['course_end_time'] == str(course_time.end_time)
                assert course_time_data['place'] == str(course_time.place)
                assert str(course_time_data['course_time_representation']) == str(course_time_representation)

    def test_if_returned_data_has_correct_values_for_exam_times(self, api_client, user_instance,
                                                                course_groups_view_url, courses,
                                                                sorted_course_with_first_course_base_course_id):
        api_client.force_login(user_instance)

        response = api_client.get(course_groups_view_url(courses[0].base_course_id))

        for course_data, course in zip(response.data, sorted_course_with_first_course_base_course_id):
            for exam_time_data, exam_time in zip(course_data['exam_times'], course.exam_times.all()):
                assert str(exam_time_data['date']).split('.')[0] == str(exam_time.date).split('.')[0]
                assert str(exam_time_data['exam_start_time']).split('.')[0] == str(exam_time.start_time).split('.')[0]
                assert str(exam_time_data['exam_end_time']).split('.')[0] == str(exam_time.end_time).split('.')[0]

    def test_if_returned_data_has_correct_values_for_teachers(self, api_client, user_instance,
                                                              course_groups_view_url, courses,
                                                              sorted_course_with_first_course_base_course_id):
        api_client.force_login(user_instance)

        response = api_client.get(course_groups_view_url(courses[0].base_course_id))

        for course_data, course in zip(response.data, sorted_course_with_first_course_base_course_id):
            for teacher_data, teacher in zip(course_data['teachers'], course.teachers.all()):
                assert teacher_data['id'] == teacher.id
                assert teacher_data['name'] == teacher.name
                assert teacher_data['teacher_image'] == teacher.image_full_path

    def test_if_returned_data_only_contains_courses_with_base_course_id(self, api_client, user_instance,
                                                                        course_groups_view_url,
                                                                        sorted_course_with_first_course_base_course_id):
        api_client.force_login(user_instance)

        response = api_client.get(
            course_groups_view_url(sorted_course_with_first_course_base_course_id[0].base_course_id))

        assert all(
            course['base_course_id'] == sorted_course_with_first_course_base_course_id[0].base_course_id for course in
            response.data)

    def test_if_returned_data_only_contains_courses_with_correct_gender(self, api_client, user_instance,
                                                                        course_groups_view_url,
                                                                        sorted_course_with_first_course_base_course_id):
        baker.make(Course, base_course=sorted_course_with_first_course_base_course_id[0].base_course, sex='F')
        baker.make(Course, base_course=sorted_course_with_first_course_base_course_id[0].base_course, sex='M')
        api_client.force_login(user_instance)

        response = api_client.get(
            course_groups_view_url(sorted_course_with_first_course_base_course_id[0].base_course_id))

        assert all(course['sex'] == user_instance.gender or course['sex'] == 'B' for course in response.data)

    def test_if_returned_data_has_correct_color_intensity(self, api_client, user_instance,
                                                          course_groups_view_url,
                                                          sorted_course_with_first_course_base_course_id):
        api_client.force_login(user=user_instance)

        response = api_client.get(
            course_groups_view_url(sorted_course_with_first_course_base_course_id[0].base_course_id))

        assert all(
            response_course['color_intensity_percentage'] == course.color_intensity_percentage for
            response_course, course in zip(response.data, sorted_course_with_first_course_base_course_id))

    def test_if_returned_data_has_correct_is_allowed(self, api_client, user_instance,
                                                          course_groups_view_url,
                                                          sorted_course_with_first_course_base_course_id):
        api_client.force_login(user=user_instance)

        response = api_client.get(
            course_groups_view_url(sorted_course_with_first_course_base_course_id[0].base_course_id))

        assert all(
            response_course['is_allowed'] == course.allowed_departments.filter(
                department__department_number=user_instance.department.department_number).exists() for
            response_course, course in zip(response.data, sorted_course_with_first_course_base_course_id))
