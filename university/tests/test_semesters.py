import pytest
from rest_framework import status
from model_bakery import baker

from accounts.models import User
from university.models import Semester


@pytest.mark.django_db
class TestSemestersListView:
    def test_if_get_request_is_status_200_for_login_user(self, api_client, simple_user, semesters_list_view_url):
        api_client.force_login(simple_user)
        response = api_client.get(semesters_list_view_url)
        assert response.status_code == status.HTTP_200_OK

    def test_if_get_request_is_status_403_for_anonymous_user(self, api_client, simple_user, semesters_list_view_url):
        response = api_client.get(semesters_list_view_url)
        assert response.status_code == status.HTTP_403_FORBIDDEN

    def test_if_post_request_is_status_405(self, api_client, simple_user, semesters_list_view_url):
        api_client.force_login(user=simple_user)
        response = api_client.post(semesters_list_view_url)
        assert response.status_code == status.HTTP_405_METHOD_NOT_ALLOWED

    def test_if_put_request_is_status_405(self, api_client, simple_user, semesters_list_view_url):
        api_client.force_login(user=simple_user)
        response = api_client.post(semesters_list_view_url)
        assert response.status_code == status.HTTP_405_METHOD_NOT_ALLOWED

    def test_if_patch_request_is_status_405(self, api_client, simple_user, semesters_list_view_url):
        api_client.force_login(user=simple_user)
        response = api_client.patch(semesters_list_view_url)
        assert response.status_code == status.HTTP_405_METHOD_NOT_ALLOWED

    def test_if_delete_request_is_status_405(self, api_client, simple_user, semesters_list_view_url):
        api_client.force_login(user=simple_user)
        response = api_client.delete(semesters_list_view_url)
        assert response.status_code == status.HTTP_405_METHOD_NOT_ALLOWED

    def test_if_get_request_returns_all_semesters(self, api_client, simple_user, semesters_list_view_url):
        api_client.force_login(user=simple_user)
        baker.make(Semester, _quantity=10)
        response = api_client.get(semesters_list_view_url)
        assert len(response.data) == 10

    def test_if_get_request_returns_semesters_with_correct_fields(self, api_client, simple_user,
                                                                  semesters_list_view_url):
        api_client.force_login(user=simple_user)

        baker.make(Semester, _quantity=10)
        response = api_client.get(semesters_list_view_url)

        assert response.data[0].keys() == {'year'}

    def test_if_get_request_returns_semesters_with_correct_data(self, api_client, simple_user, semesters_list_view_url):
        api_client.force_login(user=simple_user)
        semesters = baker.make(Semester, _quantity=10)
        # sort semesters by year:
        semesters = sorted(semesters, key=lambda semester: -semester.year)

        response = api_client.get(semesters_list_view_url)

        assert response.data[0]['year'] == semesters[0].year
        assert response.data[1]['year'] == semesters[1].year
        assert response.data[2]['year'] == semesters[2].year
        assert response.data[3]['year'] == semesters[3].year
        assert response.data[-1]['year'] == semesters[-1].year
