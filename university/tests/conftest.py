from django.contrib.auth.models import User
from django.urls import reverse
from rest_framework.test import APIClient
import pytest


@pytest.fixture
def api_client():
    return APIClient()


@pytest.fixture
def sign_up_department_list_view_url():
    return reverse('department_names')


@pytest.fixture
def department_list_view_url():
    return reverse('departments')


@pytest.fixture
def sorted_department_list_view_url():
    return reverse('sorted_department_names')


@pytest.fixture
def authenticate(api_client):
    def do_authenticate(is_staff=False):
        return api_client.force_authenticate(user=User(is_staff=is_staff, department=22))
    return do_authenticate
