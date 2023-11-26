from django.contrib.auth import get_user_model
from django.contrib.contenttypes.models import ContentType
from django.db.models.signals import post_save
from django.dispatch import receiver

from social_media.models import Profile, Notification
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
    recipient = kwargs['recipient']
    notification_type = kwargs['notification_type']
    actor = kwargs['actor']

    if notification_type == Notification.TYPE_FOLLOW:
        Notification.objects.create(
            recipient=recipient,
            actor=actor,
            notification_type=notification_type,
        )
    else:
        tweet = kwargs['tweet']
        Notification.objects.create(
            recipient=recipient,
            actor=actor,
            notification_type=notification_type,
            tweet=tweet
        )
