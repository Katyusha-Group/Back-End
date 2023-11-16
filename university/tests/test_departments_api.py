import pytest
from rest_framework import status
from model_bakery import baker

from accounts.models import User
from university.models import Department


@pytest.mark.django_db
class TestSignupDepartmentListView:
    def test_if_get_request_is_status_200(self, api_client, sign_up_department_list_view_url):
        response = api_client.get(sign_up_department_list_view_url)

        assert response.status_code == status.HTTP_200_OK

    def test_if_post_request_is_status_405(self, api_client, sign_up_department_list_view_url):
        response = api_client.post(sign_up_department_list_view_url)

        assert response.status_code == status.HTTP_405_METHOD_NOT_ALLOWED

    def test_if_put_request_is_status_405(self, api_client, sign_up_department_list_view_url):
        response = api_client.put(sign_up_department_list_view_url)

        assert response.status_code == status.HTTP_405_METHOD_NOT_ALLOWED

    def test_if_patch_request_is_status_405(self, api_client, sign_up_department_list_view_url):
        response = api_client.patch(sign_up_department_list_view_url)

        assert response.status_code == status.HTTP_405_METHOD_NOT_ALLOWED

    def test_if_delete_request_is_status_405(self, api_client, sign_up_department_list_view_url):
        response = api_client.delete(sign_up_department_list_view_url)

        assert response.status_code == status.HTTP_405_METHOD_NOT_ALLOWED

    def test_if_returned_query_set_only_contains_dn_greater_than_0(self, api_client, sign_up_department_list_view_url):
        """
        Test that the get_queryset method returns all departments with department_number greater than 0.
        """
        # Create some departments with department_number greater than 0
        baker.make(Department, name='Department 1', department_number=1)
        baker.make(Department, name='Department 2', department_number=2)
        baker.make(Department, name='Department 3', department_number=3)

        # Create some departments with department_number less than or equal to 0
        baker.make(Department, name='Department 4', department_number=0)

        # Make a GET request to the SignupDepartmentListView
        response = api_client.get(sign_up_department_list_view_url)

        # Check that the response status code is 200 OK
        assert response.status_code == status.HTTP_200_OK

        # Check that the response data contains all departments with department_number greater than 0
        assert len(response.data) == 3

    def test_if_returned_data_is_correct(self, api_client, sign_up_department_list_view_url):
        department_1 = baker.make(Department, name='Department 1', department_number=1)
        department_2 = baker.make(Department, name='Department 2', department_number=2)
        department_3 = baker.make(Department, name='Department 3', department_number=3)

        response = api_client.get(sign_up_department_list_view_url)

        assert response.data == [
            {
                'value': department_1.department_number,
                'label': department_1.name
            },
            {
                'value': department_2.department_number,
                'label': department_2.name
            },
            {
                'value': department_3.department_number,
                'label': department_3.name
            }
        ]


@pytest.mark.django_db
class TestSortedDepartmentListView:
    def test_if_get_request_with_authenticated_user_is_status_200(self, api_client, user_instance,
                                                                  sorted_department_list_view_url):
        # Authenticate the user
        api_client.force_login(user_instance)

        # Make a GET request to the SignupDepartmentListView
        response = api_client.get(sorted_department_list_view_url)

        assert response.status_code == status.HTTP_200_OK

    def test_if_get_request_with_unauthenticated_user_is_status_403(self, api_client, sorted_department_list_view_url):
        # Make a GET request to the SignupDepartmentListView
        response = api_client.get(sorted_department_list_view_url)

        assert response.status_code == status.HTTP_403_FORBIDDEN

    def test_if_put_request_is_status_405(self, api_client, user_instance, sorted_department_list_view_url):
        # Authenticate the user
        api_client.force_login(user_instance)

        # Make a PUT request to the SignupDepartmentListView
        response = api_client.put(sorted_department_list_view_url)

        assert response.status_code == status.HTTP_405_METHOD_NOT_ALLOWED

    def test_if_patch_request_is_status_405(self, api_client, user_instance, sorted_department_list_view_url):
        # Authenticate the user
        api_client.force_login(user_instance)

        # Make a PATCH request to the SignupDepartmentListView
        response = api_client.patch(sorted_department_list_view_url)

        assert response.status_code == status.HTTP_405_METHOD_NOT_ALLOWED

    def test_if_post_request_is_status_405(self, api_client, user_instance, sorted_department_list_view_url):
        # Authenticate the user
        api_client.force_login(user_instance)

        # Make a POST request to the SignupDepartmentListView
        response = api_client.post(sorted_department_list_view_url)

        assert response.status_code == status.HTTP_405_METHOD_NOT_ALLOWED

    def test_if_delete_request_is_status_405(self, api_client, user_instance, sorted_department_list_view_url):
        # Authenticate the user
        api_client.force_login(user_instance)

        # Make a DELETE request to the SignupDepartmentListView
        response = api_client.delete(sorted_department_list_view_url)

        assert response.status_code == status.HTTP_405_METHOD_NOT_ALLOWED

    def test_if_returned_data_is_sorted_by_user_department(self, api_client, sorted_department_list_view_url):
        # Create departments with different department numbers
        department1 = baker.make(Department, department_number=1)
        department2 = baker.make(Department, department_number=2)
        department3 = baker.make(Department, department_number=3)
        department4 = baker.make(Department, department_number=4)

        # Set user department to department2
        user = baker.make(User, department=department2)

        # Authenticate the user
        api_client.force_login(user)

        # Make a GET request to the SortedNamesDepartmentListView
        response = api_client.get(sorted_department_list_view_url)

        print(response.data)

        # Check that the response data contains all departments sorted by user department
        assert response.data[0]['value'] == department2.department_number
        assert response.data[1]['value'] == department1.department_number
        assert response.data[2]['value'] == department3.department_number
        assert response.data[3]['value'] == department4.department_number


@pytest.mark.django_db
class TestDepartmentsListView:
    def test_if_get_request_with_authenticated_user_is_status_200(self, api_client, user_instance,
                                                                  departments_list_view_url):
        # Authenticate the user
        api_client.force_login(user_instance)

        # Make a GET request to the SignupDepartmentListView
        response = api_client.get(departments_list_view_url)

        assert response.status_code == status.HTTP_200_OK

    def test_if_get_request_with_unauthenticated_user_is_status_403(self, api_client, departments_list_view_url):
        # Make a GET request to the SignupDepartmentListView
        response = api_client.get(departments_list_view_url)

        assert response.status_code == status.HTTP_403_FORBIDDEN

    def test_if_put_request_is_status_405(self, api_client, user_instance, departments_list_view_url):
        # Authenticate the user
        api_client.force_login(user_instance)

        # Make a PUT request to the SignupDepartmentListView
        response = api_client.put(departments_list_view_url)

        assert response.status_code == status.HTTP_405_METHOD_NOT_ALLOWED

    def test_if_patch_request_is_status_405(self, api_client, user_instance, departments_list_view_url):
        # Authenticate the user
        api_client.force_login(user_instance)

        # Make a PATCH request to the SignupDepartmentListView
        response = api_client.patch(departments_list_view_url)

        assert response.status_code == status.HTTP_405_METHOD_NOT_ALLOWED

    def test_if_post_request_is_status_405(self, api_client, user_instance, departments_list_view_url):
        # Authenticate the user
        api_client.force_login(user_instance)

        # Make a POST request to the SignupDepartmentListView
        response = api_client.post(departments_list_view_url)

        assert response.status_code == status.HTTP_405_METHOD_NOT_ALLOWED

    def test_if_delete_request_is_status_405(self, api_client, user_instance, departments_list_view_url):
        # Authenticate the user
        api_client.force_login(user_instance)

        # Make a DELETE request to the SignupDepartmentListView
        response = api_client.delete(departments_list_view_url)

        assert response.status_code == status.HTTP_405_METHOD_NOT_ALLOWED
