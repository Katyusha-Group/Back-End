import pytest
from django.contrib.auth import get_user_model
from django.core.exceptions import ValidationError
from django.db import IntegrityError
from model_bakery import baker

from social_media.models import Profile, Notification, Twitte, Follow, ReportTwitte

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



class TestTwitteModel:
    def test_str_representation(self, twitte_instance):
        expected_string = f'{twitte_instance.profile} twitted {twitte_instance.content}'
        assert str(twitte_instance) == expected_string

    def test_tweet_creation(self, profile_twitte):
        tweet_content = "This is a test tweet"
        tweet = Twitte.objects.create(profile=profile_twitte, content=tweet_content)
        assert tweet.content == tweet_content

    def test_tweet_content_validation(self, profile_twitte):
        with pytest.raises(ValidationError):
            # Assuming the max length is 280 characters
            long_content = "a" * 281
            Twitte.objects.create(profile=profile_twitte, content=long_content).full_clean()

    def test_tweet_likes(self, profile_twitte, other_profile_twitte):
        tweet = baker.make(Twitte, profile=profile_twitte)

        tweet.like(other_profile_twitte)
        assert tweet.is_liked_by(other_profile_twitte)

        tweet.unlike(other_profile_twitte)
        assert not tweet.is_liked_by(other_profile_twitte)

    def test_tweet_reply_and_conversation(self, profile_twitte):
        parent_tweet = baker.make(Twitte, profile=profile_twitte)
        reply_tweet = baker.make(Twitte, profile=profile_twitte, parent=parent_tweet)

        assert reply_tweet.get_parent() == parent_tweet
        assert parent_tweet.get_children().filter(pk=reply_tweet.pk).exists()

    def test_tweet_counts(self, profile_twitte):
        tweet = baker.make(Twitte, profile=profile_twitte)
        for _ in range(5):
            Twitte.objects.create(profile=profile_twitte, parent=tweet)

        assert tweet.get_children_count() == 5

    def test_tweet_report_count(self, profile_twitte, other_profile_twitte, twitte_instance):
        ReportTwitte.objects.create(reporter=profile_twitte, twitte=twitte_instance, reason='S')
        ReportTwitte.objects.create(reporter=other_profile_twitte, twitte=twitte_instance, reason='S')
        assert twitte_instance.get_reports_count() == 2
        
    def test_tweet_likes_count(self, profile_twitte, other_profile_twitte, twitte_instance):
        twitte_instance.like(profile_twitte)
        twitte_instance.like(other_profile_twitte)
        assert twitte_instance.get_likes_count() == 2

    def test_tweet_replies_count(self, profile_twitte, twitte_instance):
        for _ in range(5):
            Twitte.objects.create(profile=profile_twitte, parent=twitte_instance)

        assert twitte_instance.get_children_count() == 5
        

class TestReportTwitteModel:

    def test_str_representation(self, reporter_profile, twitte_instance):
        report = baker.make(ReportTwitte, reporter=reporter_profile, twitte=twitte_instance, reason='S')
        expected_string = f'{report.reporter} reported {report.twitte} as {report.get_reason_display()}'
        assert str(report) == expected_string

    def test_report_creation(self, reporter_profile):
        twitte_instance = baker.make(Twitte, profile=reporter_profile)
        report = ReportTwitte.objects.create(reporter=reporter_profile, twitte=twitte_instance, reason='S')
        assert report.reason == 'S'
    
    def test_unique_constraint(self, reporter_profile):
        twitte_instance = baker.make(Twitte, profile=reporter_profile)
        ReportTwitte.objects.create(reporter=reporter_profile, twitte=twitte_instance, reason='S')
        
        with pytest.raises(IntegrityError):
            ReportTwitte.objects.create(reporter=reporter_profile, twitte=twitte_instance, reason='S')

    def test_reason_field(self, reporter_profile, twitte_instance):
        report_twitte = ReportTwitte(reporter=reporter_profile, twitte=twitte_instance, reason='X')
        
        with pytest.raises(ValidationError):
            report_twitte.full_clean()
            report_twitte.save()

    def test_relationships(self, reporter_profile, twitte_instance):
        report_twitte = ReportTwitte.objects.create(reporter=reporter_profile, twitte=twitte_instance, reason='S')
        assert report_twitte.reporter == reporter_profile
        assert report_twitte.twitte == twitte_instance
