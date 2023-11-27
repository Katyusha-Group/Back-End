from django.contrib.auth import get_user_model
from django.contrib.contenttypes.models import ContentType
from django.db.models.signals import post_save
from django.dispatch import receiver

from social_media.models import Profile, Notification, Follow
from university.models import Teacher, BaseCourse
from accounts.models import User
from social_media.signals import send_notification


@receiver(post_save, sender=User)
@receiver(post_save, sender=Teacher)
@receiver(post_save, sender=BaseCourse)
def create_profile(sender, **kwargs):
    if kwargs['created']:
        content_type = ContentType.objects.get_for_model(sender)
        Profile.objects.create(content_type=content_type, object_id=kwargs['instance'].pk)


@receiver(send_notification)
def send_notification_handler(sender, **kwargs):
    notification_type = kwargs['notification_type']
    actor = kwargs['actor']
    profiles = Follow.objects.filter(following=actor).prefetch_related('follower').all()
    followers_profile = [follow.follower for follow in profiles]

    notifications = []
    for profile in followers_profile:
        if notification_type == Notification.TYPE_FOLLOW:
            notifications.append(Notification(
                recipient=profile,
                actor=actor,
                notification_type=notification_type,
            ))
        else:
            tweet = kwargs['tweet']
            notifications.append(Notification(
                recipient=profile,
                actor=actor,
                notification_type=notification_type,
                tweet=tweet
            ))
    Notification.objects.bulk_create(notifications)
