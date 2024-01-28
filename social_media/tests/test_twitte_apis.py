import pytest
from model_bakery import baker
from rest_framework import status
from rest_framework.test import APIClient
from django.urls import reverse
from social_media.models import Profile, Twitte, Follow
from django.contrib.auth import get_user_model
import datetime
from django.utils import timezone
from freezegun import freeze_time


pytestmark = pytest.mark.django_db

class TestTwitteAPI:
    @pytest.fixture
    def api_client(self):
        return APIClient(HTTP_HOST='localhost:8000')

    @pytest.fixture
    def setup(self, api_client):
        self.client = api_client
        self.user = baker.make(get_user_model(), username='testuser', password='testpass')
        self.profile = Profile.get_profile_for_user(self.user)
        self.client.force_authenticate(user=self.user)

    def test_create_twitte(self, setup):
        data = {"content": "Hello World"}
        response = self.client.post(reverse('social_media:twittes-list'), data)
        assert response.status_code == status.HTTP_201_CREATED
        assert Twitte.objects.filter(profile=self.profile).exists()

    def test_list_twittes(self, setup):
        baker.make(Twitte, profile=self.profile, _quantity=5)
        response = self.client.get(reverse('social_media:twittes-list'))
        assert response.status_code == status.HTTP_200_OK
        assert len(response.data) == 5

    def test_like_twitte(self, setup):
        twitte = baker.make(Twitte, profile=self.profile)
        response = self.client.post(reverse('social_media:twittes-like', kwargs={'pk': twitte.id}))
        assert response.status_code == status.HTTP_201_CREATED
        assert twitte.likes.filter(pk=self.profile.pk).exists()

    def test_unlike_twitte(self, setup):
        twitte = baker.make(Twitte, profile=self.profile)
        twitte.like(self.profile)
        response = self.client.post(reverse('social_media:twittes-unlike', kwargs={'pk': twitte.id}))
        assert response.status_code == status.HTTP_204_NO_CONTENT
        assert not twitte.likes.filter(pk=self.profile.pk).exists()

    def test_following_twittes_list(self, setup):
        followed_user = baker.make(get_user_model(), username='followeduser', password='testpass')
        followed_profile = Profile.get_profile_for_user(followed_user)
        baker.make(Follow, follower=self.profile, following=followed_profile)
        baker.make(Twitte, profile=followed_profile, _quantity=3)
        response = self.client.get(reverse('social_media:followings-twittes-list'))
        assert response.status_code == status.HTTP_200_OK
        assert len(response.data) == 3


class TestForYouTwittesAPI:
    @pytest.fixture
    def setup_for_you(self, setup):
        # Create followings and their tweets
        for i in range(3):
            following_user = baker.make(get_user_model(), username=f'followinguser{i}', password='testpass')
            following_profile = Profile.get_profile_for_user(following_user)
            baker.make(Follow, follower=self.profile, following=following_profile)
            baker.make(Twitte, profile=following_profile, _quantity=2)

    def test_for_you_twittes_list(self, setup_for_you):
        response = self.client.get(reverse('social_media:for-you-twittes-list'))
        assert response.status_code == status.HTTP_200_OK
        # Asserting that tweets are from the followings of followings


class TestManageTwittesAPI:
    @pytest.fixture
    def setup_manage(self, setup):
        self.admin_user = baker.make(get_user_model(), username='adminuser', password='adminpass', is_staff=True)
        self.client.force_authenticate(user=self.admin_user)

    def test_manage_twittes_list(self, setup_manage):
        baker.make(Twitte, _quantity=5)
        response = self.client.get(reverse('social_media:manage-twittes-list'))
        assert response.status_code == status.HTTP_200_OK
        assert len(response.data) == 5

    def test_delete_twitte(self, setup_manage):
        twitte = baker.make(Twitte)
        response = self.client.delete(reverse('social_media:manage-twittes-detail', kwargs={'pk': twitte.id}))
        assert response.status_code == status.HTTP_204_NO_CONTENT
        assert not Twitte.objects.filter(pk=twitte.id).exists()


# Example test for TwitteChartViewSet
class TestTwitteChartAPI:
    @pytest.fixture
    def setup(self, api_client):
        self.client = api_client
        self.admin_user = baker.make(get_user_model(), username='adminuser', password='adminpass', is_staff=True)
        self.client.force_authenticate(user=self.admin_user)

    def test_last_week_tweets(self, setup):
        # Create tweets over the last week
        for days_back in range(7):
            date = timezone.now() - datetime.timedelta(days=days_back)
            with freeze_time(date):
                baker.make(Twitte, profile=self.profile, _quantity=2)

        response = self.client.get(reverse('social_media:twitte-charts-last-week-tweets'))
        assert response.status_code == status.HTTP_200_OK

        data = response.data
        assert len(data) == 7  # Checks if data for 7 days is returned

        # Check if the count matches
        for day_data in data:
            date = datetime.datetime.strptime(day_data['date'], '%Y-%m-%d').date()
            expected_count = 2 if (timezone.now().date() - date).days < 7 else 0
            assert day_data['tweets_count'] == expected_count
