from django.urls import reverse
from rest_framework import status

import pytest
from model_bakery import baker

from accounts.models import User
from university.models import Department


@pytest.mark.django_db
class TestSignupDepartmentListView:
    def setUp(self):
        self.url = reverse('department_names')

    def test_if_get_request_is_status_200(self, api_client):
        response = api_client.get(self.url)

        assert response.status_code == status.HTTP_200_OK

    def test_if_post_request_is_status_405(self, api_client):
        response = api_client.post(self.url)

        assert response.status_code == status.HTTP_405_METHOD_NOT_ALLOWED

    def test_if_put_request_is_status_405(self, api_client):
        response = api_client.put(self.url)

        assert response.status_code == status.HTTP_405_METHOD_NOT_ALLOWED

    def test_if_patch_request_is_status_405(self, api_client):
        response = api_client.patch(self.url)

        assert response.status_code == status.HTTP_405_METHOD_NOT_ALLOWED

    def test_if_delete_request_is_status_405(self, api_client):
        response = api_client.delete(self.url)

        assert response.status_code == status.HTTP_405_METHOD_NOT_ALLOWED

    def test_if_returned_query_set_only_contains_dn_greater_than_0(self, api_client):
        """
        Test that the get_queryset method returns all departments with department_number greater than 0.
        """
        # Create some departments with department_number greater than 0
        Department.objects.create(name='Department 1', department_number=1)
        Department.objects.create(name='Department 2', department_number=2)
        Department.objects.create(name='Department 3', department_number=3)

        # Create some departments with department_number less than or equal to 0
        Department.objects.create(name='Department 4', department_number=0)
        Department.objects.create(name='Department 5', department_number=-1)

        # Make a GET request to the SignupDepartmentListView
        response = api_client.get(self.url)

        # Check that the response status code is 200 OK
        assert response.status_code == status.HTTP_200_OK

        # Check that the response data contains all departments with department_number greater than 0
        assert len(response.data) == 3

    def test_if_returned_data_is_correct(self, api_client):
        departments = baker.make(Department, _quantity=3)

        response = api_client.get(self.url)

        assert response.data == [
            {
                'value': departments[0].department_number,
                'label': departments[0].name
            },
            {
                'value': departments[1].department_number,
                'label': departments[1].name
            },
            {
                'value': departments[2].department_number,
                'label': departments[2].name
            }
        ]


@pytest.mark.django_db
class TestSortedDepartmentListView:
    def setUp(self):
        self.url = reverse('sorted_department_names')
        self.user = baker.make(User)

    def test_if_get_request_with_authenticated_user_is_status_200(self):
        # Authenticate the user
        self.client.force_login(self.user)

        # Make a GET request to the SignupDepartmentListView
        response = self.client.get(self.url)

        assert response.status_code == status.HTTP_200_OK

    def test_if_get_request_with_unauthenticated_user_is_status_403(self):
        # Make a GET request to the SignupDepartmentListView
        response = self.client.get(self.url)

        assert response.status_code == status.HTTP_403_FORBIDDEN

    def test_if_put_request_is_status_405(self):
        # Authenticate the user
        self.client.force_login(self.user)

        # Make a PUT request to the SignupDepartmentListView
        response = self.client.put(self.url)

        assert response.status_code == status.HTTP_405_METHOD_NOT_ALLOWED

    def test_if_patch_request_is_status_405(self):
        # Authenticate the user
        self.client.force_login(self.user)

        # Make a PATCH request to the SignupDepartmentListView
        response = self.client.patch(self.url)

        assert response.status_code == status.HTTP_405_METHOD_NOT_ALLOWED

    def test_if_post_request_is_status_405(self):
        # Authenticate the user
        self.client.force_login(self.user)

        # Make a POST request to the SignupDepartmentListView
        response = self.client.post(self.url)

        assert response.status_code == status.HTTP_405_METHOD_NOT_ALLOWED

    def test_if_delete_request_is_status_405(self):
        # Authenticate the user
        self.client.force_login(self.user)

        # Make a DELETE request to the SignupDepartmentListView
        response = self.client.delete(self.url)

        assert response.status_code == status.HTTP_405_METHOD_NOT_ALLOWED

    def test_if_returned_data_is_sorted_by_user_department(self):
        # Create departments with different department numbers
        department1 = baker.make(Department, department_number=1)
        department2 = baker.make(Department, department_number=2)
        department3 = baker.make(Department, department_number=3)
        department4 = baker.make(Department, department_number=4)

        # Set user department to department2
        self.user.department = department2
        self.user.save()

        # Make a GET request to the SortedNamesDepartmentListView
        response = self.client.get(self.url)

        # Check that the response data contains all departments sorted by user department
        assert response.data[0]['value'] == department2.department_number
        assert response.data[1]['value'] == department1.department_number
        assert response.data[2]['value'] == department3.department_number
        assert response.data[3]['value'] == department4.department_number


@pytest.mark.django_db
class TestDepartmentsListView:
    def setUp(self):
        self.url = reverse('departments')
        self.user = baker.make(User)

    def test_if_get_request_with_authenticated_user_is_status_200(self):
        # Authenticate the user
        self.client.force_login(self.user)

        # Make a GET request to the SignupDepartmentListView
        response = self.client.get(self.url)

        assert response.status_code == status.HTTP_200_OK

    def test_if_get_request_with_unauthenticated_user_is_status_403(self):
        # Make a GET request to the SignupDepartmentListView
        response = self.client.get(self.url)

        assert response.status_code == status.HTTP_403_FORBIDDEN

    def test_if_put_request_is_status_405(self):
        # Authenticate the user
        self.client.force_login(self.user)

        # Make a PUT request to the SignupDepartmentListView
        response = self.client.put(self.url)

        assert response.status_code == status.HTTP_405_METHOD_NOT_ALLOWED

    def test_if_patch_request_is_status_405(self):
        # Authenticate the user
        self.client.force_login(self.user)

        # Make a PATCH request to the SignupDepartmentListView
        response = self.client.patch(self.url)

        assert response.status_code == status.HTTP_405_METHOD_NOT_ALLOWED

    def test_if_post_request_is_status_405(self):
        # Authenticate the user
        self.client.force_login(self.user)

        # Make a POST request to the SignupDepartmentListView
        response = self.client.post(self.url)

        assert response.status_code == status.HTTP_405_METHOD_NOT_ALLOWED

    def test_if_delete_request_is_status_405(self):
        # Authenticate the user
        self.client.force_login(self.user)

        # Make a DELETE request to the SignupDepartmentListView
        response = self.client.delete(self.url)

        assert response.status_code == status.HTTP_405_METHOD_NOT_ALLOWED
