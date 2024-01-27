import pytest
from django.contrib.contenttypes.models import ContentType
from model_bakery import baker
from rest_framework.test import APIClient
from django.urls import reverse
from social_media.models import Profile, Follow
from django.contrib.auth import get_user_model

from university.models import BaseCourse, Teacher

pytestmark = pytest.mark.django_db


class TestProfileAPI:
    @pytest.fixture
    def api_client(self):
        return APIClient(HTTP_HOST='localhost:8000')

    @pytest.fixture
    def setup(self, api_client):
        self.client = api_client
        self.user = baker.make(get_user_model(), username='testuser', password='testpass')
        self.profile = Profile.get_profile_for_user(self.user)
        self.client.force_authenticate(user=self.user)

    def test_view_profile(self, setup):
        new_user = baker.make(get_user_model(), username='newuser', password='testpass')
        response = self.client.get(reverse('social_media:profiles-view-profile', kwargs={'username': 'newuser'}))
        assert response.status_code == 200
        assert response.data['username'] == 'newuser'

    def test_update_profile_name(self, setup):
        response = self.client.patch(reverse('social_media:profiles-update-profile'), {'name': 'Updated Name'})
        assert response.status_code == 200
        assert response.data['name'] == 'Updated Name'

    def test_update_profile_is_private(self, setup):
        response = self.client.patch(reverse('social_media:profiles-update-profile'), {'is_private': True})
        assert response.status_code == 200
        assert response.data['is_private'] is True

    def test_follow(self, setup):
        another_user = baker.make(get_user_model(), username='anotheruser', password='testpass')
        another_profile = Profile.get_profile_for_user(another_user)
        response = self.client.post(reverse('social_media:profiles-follow', kwargs={'username': 'anotheruser'}))
        assert response.status_code == 201
        assert Follow.objects.filter(follower=self.profile, following=another_profile).exists()

    def test_follow_not_found(self, setup):
        response = self.client.post(reverse('social_media:profiles-follow', kwargs={'username': 'anotheruser'}))
        assert response.status_code == 400

    def test_unfollow(self, setup):
        another_user = baker.make(get_user_model(), username='anotheruser', password='testpass')
        another_profile = Profile.get_profile_for_user(another_user)
        baker.make(Follow, follower=self.profile, following=another_profile)
        response = self.client.post(reverse('social_media:profiles-unfollow', kwargs={'username': 'anotheruser'}))
        assert response.status_code == 204
        assert not Follow.objects.filter(follower=self.profile, following=another_profile).exists()

    def test_unfollow_not_found(self, setup):
        response = self.client.post(reverse('social_media:profiles-unfollow', kwargs={'username': 'anotheruser'}))
        assert response.status_code == 400

    def test_unfollow_not_followed(self, setup):
        another_user = baker.make(get_user_model(), username='anotheruser', password='testpass')
        response = self.client.post(reverse('social_media:profiles-unfollow', kwargs={'username': 'anotheruser'}))
        assert response.status_code == 400

    def test_list_profiles(self, setup):
        response = self.client.get(reverse('social_media:profiles-list'))
        assert response.status_code == 200

    def test_view_my_profile(self, setup):
        response = self.client.get(reverse('social_media:profiles-view-my-profile'))
        assert response.status_code == 200
        assert response.data['username'] == self.profile.username

    def test_view_followers(self, setup):
        another_user = baker.make(get_user_model(), username='anotheruser', password='testpass')
        another_profile = Profile.get_profile_for_user(another_user)
        another_profile.name = 'Another User'
        another_profile.save()

        baker.make(Follow, follower=self.profile, following=another_profile)
        response = self.client.get(
            reverse('social_media:profiles-view-followers', kwargs={'username': another_profile.username}))
        assert response.status_code == 200
        assert len(response.data) == 1
        assert response.data[0]['username'] == self.profile.username

    def test_view_following(self, setup):
        another_user = baker.make(get_user_model(), username='anotheruser', password='testpass')
        another_profile = Profile.get_profile_for_user(another_user)
        baker.make(Follow, follower=another_profile, following=self.profile)

        response = self.client.get(
            reverse('social_media:profiles-view-following', kwargs={'username': another_profile.username}))

        assert response.status_code == 200
        assert len(response.data) == 1
        assert response.data[0]['username'] == self.profile.username

    def test_view_followers_you_follow(self, setup):
        another_user = baker.make(get_user_model(), username='anotheruser', password='testpass')
        another_profile = Profile.get_profile_for_user(another_user)
        baker.make(Follow, follower=self.profile, following=another_profile)
        user2 = baker.make(get_user_model(), username='user2', password='testpass')
        profile2 = Profile.get_profile_for_user(user2)
        baker.make(Follow, follower=self.profile, following=profile2)
        baker.make(Follow, follower=profile2, following=another_profile)

        response = self.client.get(
            reverse('social_media:profiles-view-followers-you-follow', kwargs={'username': 'anotheruser'}))

        assert response.status_code == 200
        assert len(response.data['followers_you_follow']) == 1
        assert response.data['followers_you_follow'][0]['username'] == user2.username

    def test_search_profiles(self, setup):
        baker.make(get_user_model(), username='anotheruser', password='testpass')
        response = self.client.get(reverse('social_media:profiles-list'), {'search': 'anotheruser'})
        assert response.status_code == 200
        assert len(response.data) == 1
        assert response.data[0]['username'] == 'anotheruser'

    @pytest.mark.skip(reason='Need check')
    def test_view_course_timeline(self, setup):
        base_course = baker.make(BaseCourse, name='Test Course', course_number=1234567)
        base_course_profile = Profile.objects.filter(content_type=ContentType.objects.get_for_model(BaseCourse),
                                                     object_id=base_course.pk).first()
        try:
            response = self.client.get(reverse('social_media:profiles-view-course-timeline',
                                               kwargs={'username': base_course_profile.username}))
            assert response.status_code == 200
        except ConnectionError:
            pass

    def test_view_course_timeline_not_found(self, setup):
        response = self.client.get(reverse('social_media:profiles-view-course-timeline',
                                           kwargs={'username': 'testcourse'}))
        assert response.status_code == 404

    def test_view_course_timeline_not_course(self, setup):
        response = self.client.get(reverse('social_media:profiles-view-course-timeline',
                                           kwargs={'username': self.profile.username}))
        assert response.status_code == 400

    @pytest.mark.skip(reason='Need check')
    def test_view_teacher_timeline(self, setup):
        teacher = baker.make(Teacher, name='Test Teacher')
        teacher_profile = Profile.objects.filter(content_type=ContentType.objects.get_for_model(Teacher),
                                                 object_id=teacher.pk).first()
        try:
            response = self.client.get(reverse('social_media:profiles-view-teacher-timeline',
                                               kwargs={'username': teacher_profile.username}))
            assert response.status_code == 200
        except ConnectionError:
            pass

    def test_view_teacher_timeline_not_found(self, setup):
        response = self.client.get(reverse('social_media:profiles-view-teacher-timeline',
                                           kwargs={'username': 'testteacher'}))
        assert response.status_code == 404

    def test_view_teacher_timeline_not_teacher(self, setup):
        response = self.client.get(reverse('social_media:profiles-view-teacher-timeline',
                                           kwargs={'username': self.profile.username}))
        assert response.status_code == 400

    def test_view_student_calendar(self, setup):
        response = self.client.get(reverse('social_media:profiles-view-student-calendar',
                                           kwargs={'username': self.profile.username}))
        assert response.status_code == 200

    def test_view_student_calendar_not_student(self, setup):
        teacher = baker.make(Teacher, name='Test Teacher')
        teacher_profile = Profile.objects.filter(content_type=ContentType.objects.get_for_model(Teacher),
                                                 object_id=teacher.pk).first()
        try:
            response = self.client.get(reverse('social_media:profiles-view-student-calendar',
                                               kwargs={'username': teacher_profile.username}))
            assert response.status_code == 400
        except ConnectionError:
            pass

    def test_view_student_calendar_not_found(self, setup):
        response = self.client.get(reverse('social_media:profiles-view-student-calendar',
                                           kwargs={'username': 'teststudent'}))
        assert response.status_code == 404
