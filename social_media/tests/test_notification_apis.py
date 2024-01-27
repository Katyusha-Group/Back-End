import pytest
from model_bakery import baker
from rest_framework import status
from rest_framework.test import APIClient
from django.urls import reverse
from social_media.models import Profile, Notification
from django.contrib.auth import get_user_model

from university.models import BaseCourse, Teacher

pytestmark = pytest.mark.django_db


class TestNotificationAPI:
    @pytest.fixture
    def api_client(self):
        return APIClient(HTTP_HOST='localhost:8000')

    @pytest.fixture
    def setup(self, api_client):
        self.client = api_client
        self.user = baker.make(get_user_model(), username='testuser', password='testpass')
        self.profile = Profile.get_profile_for_user(self.user)
        self.client.force_authenticate(user=self.user)

    def test_get_notifications_200_for_authenticated_user(self, setup):
        response = self.client.get(reverse('social_media:notifications-list'))
        assert response.status_code == status.HTTP_200_OK

    def test_get_notifications_403_for_unauthenticated_user(self, api_client):
        response = api_client.get(reverse('social_media:notifications-list'))
        assert response.status_code == status.HTTP_403_FORBIDDEN

    def test_get_unread_notifications_count_200_for_authenticated_user(self, setup):
        response = self.client.get(reverse('social_media:notifications-unread-count'))
        assert response.status_code == status.HTTP_200_OK

    def test_get_unread_notifications_count_403_for_unauthenticated_user(self, api_client):
        response = api_client.get(reverse('social_media:notifications-unread-count'))
        assert response.status_code == status.HTTP_403_FORBIDDEN

    def test_notification_is_marked_as_read_after_getting_it(self, setup):
        actor = baker.make(get_user_model(), username='actor', password='testpass')
        actor_profile = Profile.get_profile_for_user(actor)
        notification = baker.make(Notification, recipient=self.profile, actor=actor_profile,
                                  notification_type=Notification.TYPE_FOLLOW)
        response = self.client.get(reverse('social_media:notifications-list'))
        assert response.status_code == status.HTTP_200_OK
        assert response.data[0]['read'] is False
        notification.refresh_from_db()
        assert notification.read is True

    def test_get_notifications_200_for_authenticated_user(self, setup):
        response = self.client.get(reverse('social_media:notifications-list'))
        assert response.status_code == status.HTTP_200_OK

    def test_unread_notifications_count(self, setup):
        actor = baker.make(get_user_model(), username='actor', password='testpass')
        actor_profile = Profile.get_profile_for_user(actor)
        notification = baker.make(Notification, recipient=self.profile, actor=actor_profile,
                                  notification_type=Notification.TYPE_FOLLOW)
        response = self.client.get(reverse('social_media:notifications-unread-count'))
        assert response.status_code == status.HTTP_200_OK
        assert response.data['count'] == 1
        notification.read = True
        notification.save()
        response = self.client.get(reverse('social_media:notifications-unread-count'))
        assert response.status_code == status.HTTP_200_OK
        assert response.data['count'] == 0

    def test_unread_notifications_count_after_getting_them(self, setup):
        actor = baker.make(get_user_model(), username='actor', password='testpass')
        actor_profile = Profile.get_profile_for_user(actor)
        notification = baker.make(Notification, recipient=self.profile, actor=actor_profile,
                                  notification_type=Notification.TYPE_FOLLOW)
        response = self.client.get(reverse('social_media:notifications-list'))
        assert response.status_code == status.HTTP_200_OK
        assert response.data[0]['read'] is False
        notification.refresh_from_db()
        assert notification.read is True
        response = self.client.get(reverse('social_media:notifications-unread-count'))
        assert response.status_code == status.HTTP_200_OK
        assert response.data['count'] == 0
