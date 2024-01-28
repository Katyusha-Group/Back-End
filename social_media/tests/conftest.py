import random

from accounts.models import User
from django.urls import reverse
from model_bakery import baker
from rest_framework.test import APIClient
import pytest

from social_media.models import Profile, Twitte


@pytest.fixture
def api_client():
    return APIClient()


@pytest.fixture
def user_instance():
    return baker.make(User, gender='M')


@pytest.fixture
def user_with_department(departments):
    return baker.make(User, department=departments[0], gender='M')


@pytest.fixture
def recipient_profile():
    user = baker.make(User, gender='F', email='recipient@gmail.com')
    return Profile.get_profile_for_user(user)


@pytest.fixture
def actor_profile():
    user = baker.make(User, gender='M', email='actor@gmail.com')
    return Profile.get_profile_for_user(user)

@pytest.fixture
def profile_twitte():
    user = baker.make(User, gender='M', email='profile_twitte@gmail.com')
    return Profile.get_profile_for_user(user)

@pytest.fixture
def other_profile_twitte():
    user = baker.make(User, gender='M', email='other_profile_twitte@gmail.com')
    return Profile.get_profile_for_user(user)

@pytest.fixture
def twitte_instance(profile_twitte):
    return baker.make(Twitte, profile=profile_twitte)

@pytest.fixture
def other_twitte_instance(other_profile_twitte):
    return baker.make(Twitte, profile=other_profile_twitte)

@pytest.fixture
def reporter_profile():
    user = baker.make(User, gender='M', email='reporter_profile@gmail.com')
    return Profile.get_profile_for_user(user)

@pytest.fixture
def to_report_twitte_instance(profile_twitte):
    return baker.make(Twitte, profile=profile_twitte)

def tweet():
    return baker.make(Twitte)


@pytest.fixture
def authenticate(api_client):
    def do_authenticate(is_staff=False):
        return api_client.force_authenticate(user=User(is_staff=is_staff, department=22))

    return do_authenticate
