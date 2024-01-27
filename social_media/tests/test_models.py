import pytest
from django.contrib.auth import get_user_model
from django.core.exceptions import ValidationError
from model_bakery import baker

from social_media.models import Profile, Notification, Twitte, Follow

pytestmark = pytest.mark.django_db


class TestProfileModel:
    def test_return_str(self, user_instance):
        profile = Profile.get_profile_for_user(user_instance)
        assert str(profile) == user_instance.email.split('@')[0]

    def test_save(self, user_instance):
        profile = Profile.get_profile_for_user(user_instance)
        assert profile.name == user_instance.get_default_profile_name()

    def test_get_image_url(self, user_instance):
        profile = Profile.get_profile_for_user(user_instance)
        domain = 'localhost:8000'
        profile.image = None
        profile.save()
        assert profile.get_image_url(domain) == f'http://{domain}' + '/media/profile_pics/default.png'

    def test_determine_image(self, user_instance):
        profile = Profile.get_profile_for_user(user_instance)
        assert profile.determine_image(profile.image) == profile.image

    def test_determine_name(self, user_instance):
        profile = Profile.get_profile_for_user(user_instance)
        assert profile.determine_name(profile.name) == profile.name

    def test_determine_username(self, user_instance):
        profile = Profile.get_profile_for_user(user_instance)
        assert profile.determine_username(profile.username) == profile.username

    def test_determine_profile_type(self, user_instance):
        profile = Profile.get_profile_for_user(user_instance)
        assert profile.determine_profile_type() == profile.profile_type


class TestNotificationModel:
    def test_return_str(self, actor_profile, recipient_profile):
        tweet = baker.make(Twitte, content='Test tweet', profile=recipient_profile)
        notification_obj = baker.make(Notification, recipient=recipient_profile, actor=actor_profile,
                                      tweet=tweet, notification_type=Notification.TYPE_LIKE)
        assert str(notification_obj) == 'recipient got notification L'

    def test_save(self, actor_profile, recipient_profile):
        with pytest.raises(ValidationError):
            baker.make(Notification, recipient=recipient_profile, actor=actor_profile,
                       notification_type=Notification.TYPE_FOLLOW,
                       tweet=baker.make(Twitte, profile=recipient_profile)).full_clean()
        with pytest.raises(ValidationError):
            baker.make(Notification, recipient=recipient_profile, actor=actor_profile,
                       notification_type=Notification.TYPE_LIKE).full_clean()

    def test_get_delta_time(self, actor_profile, recipient_profile):
        tweet = baker.make(Twitte, content='Test tweet', profile=recipient_profile)
        notification = baker.make(Notification, recipient=recipient_profile, actor=actor_profile,
                                  tweet=tweet, notification_type=Notification.TYPE_LIKE)
        assert isinstance(notification.get_delta_time(), str)

    def test_mark_as_read(self, actor_profile, recipient_profile):
        tweet = baker.make(Twitte, content='Test tweet', profile=recipient_profile)
        notification = baker.make(Notification, recipient=recipient_profile, actor=actor_profile,
                                  tweet=tweet, notification_type=Notification.TYPE_LIKE)
        notification.mark_as_read()
        assert notification.read is True

    def test_get_message_like(self, actor_profile, recipient_profile):
        tweet = baker.make(Twitte, content='Test tweet', profile=recipient_profile)
        notification = baker.make(Notification, recipient=recipient_profile, actor=actor_profile,
                                  notification_type=Notification.TYPE_LIKE, tweet=tweet)
        assert notification.get_message() == f'{actor_profile} پست شما را پسندید'


class TestFollowModel:
    def test_return_str(self, actor_profile, recipient_profile):
        follow = baker.make(Follow, follower=actor_profile, following=recipient_profile)
        assert str(follow) == 'actor follows recipient'
