import pytest
from django.contrib.auth import get_user_model
from django.core.exceptions import ValidationError
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


@pytest.mark.skip
class TestTwitteModel:

    def test_str_representation(self, twitte_instance):
        expected_string = f'{twitte_instance.profile} twitted {twitte_instance.content}'
        assert str(twitte_instance) == expected_string

    def test_tweet_creation(self, profile):
        tweet_content = "This is a test tweet"
        tweet = Twitte.objects.create(profile=profile, content=tweet_content)
        assert tweet.content == tweet_content

    def test_tweet_content_validation(self, profile):
        with pytest.raises(ValidationError):
            # Assuming the max length is 280 characters
            long_content = "a" * 281
            Twitte.objects.create(profile=profile, content=long_content).full_clean()

    def test_tweet_likes(self, profile):
        tweet = baker.make(Twitte, profile=profile)
        other_profile = baker.make(Profile)

        tweet.like(other_profile)
        assert tweet.is_liked_by(other_profile)

        tweet.unlike(other_profile)
        assert not tweet.is_liked_by(other_profile)

    def test_tweet_reply_and_conversation(self, profile):
        parent_tweet = baker.make(Twitte, profile=profile)
        reply_tweet = baker.make(Twitte, profile=profile, parent=parent_tweet)

        assert reply_tweet.get_parent() == parent_tweet
        assert parent_tweet.get_children().filter(pk=reply_tweet.pk).exists()

    def test_tweet_counts(self, profile):
        tweet = baker.make(Twitte, profile=profile)
        for _ in range(5):
            baker.make(Twitte, parent=tweet)

        assert tweet.get_children_count() == 5
        # Additional counts (likes, replies) can be tested similarly

    def test_tweet_report_count(self, profile, twitte):
        # Assuming ReportTwitte model and fixtures are set up
        for _ in range(3):
            baker.make('social_media.ReportTwitte', twitte=twitte)

        assert twitte.get_reports_count() == 3
        
    def test_tweet_likes_count(self, profile):
        tweet = baker.make(Twitte, profile=profile)
        for _ in range(3):
            liker = baker.make(Profile)
            tweet.like(liker)

        assert tweet.get_likes_count() == 3

    def test_tweet_replies_count(self, profile):
        parent_tweet = baker.make(Twitte, profile=profile)
        for _ in range(4):
            baker.make(Twitte, parent=parent_tweet)

        assert parent_tweet.get_replies_count() == 4

    def test_tweet_reports_count(self, profile, twitte):
        # Assuming ReportTwitte model and fixtures are set up
        for _ in range(5):
            reporter = baker.make(Profile)
            baker.make('social_media.ReportTwitte', twitte=twitte, reporter=reporter)

        assert twitte.get_reports_count() == 5
        
@pytest.mark.skip
class TestReportTwitteModel:

    def test_str_representation(self, report_twitte_instance):
        expected_string = f'{report_twitte_instance.reporter} reported {report_twitte_instance.twitte} as {report_twitte_instance.reason}'
        assert str(report_twitte_instance) == expected_string

    def test_report_creation(self, profile, twitte):
        report_reason = 'S'
        report = ReportTwitte.objects.create(reporter=profile, twitte=twitte, reason=report_reason)
        assert report.reason == report_reason

    def test_unique_constraint(self, profile, twitte):
        ReportTwitte.objects.create(reporter=profile, twitte=twitte, reason='S')
        with pytest.raises(ValidationError):
            ReportTwitte.objects.create(reporter=profile, twitte=twitte, reason='S').full_clean()

    def test_reason_field(self, profile, twitte):
        # Test if reason is one of the specified choices
        report = ReportTwitte.objects.create(reporter=profile, twitte=twitte, reason='S')
        assert report.reason in dict(ReportTwitte.REASON_TYPES)

    def test_relationships(self, profile, twitte):
        report = ReportTwitte.objects.create(reporter=profile, twitte=twitte, reason='S')
        assert report.reporter == profile
        assert report.twitte == twitte
