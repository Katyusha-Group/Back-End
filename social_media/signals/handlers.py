from django.contrib.auth import get_user_model
from django.contrib.contenttypes.models import ContentType
from django.db.models.signals import post_save
from django.dispatch import receiver

from social_media.models import Profile
from university.models import Teacher, BaseCourse
from accounts.models import User


@receiver(post_save, sender=User)
@receiver(post_save, sender=Teacher)
@receiver(post_save, sender=BaseCourse)
def create_profile(sender, **kwargs):
    if kwargs['created']:
        content_type = ContentType.objects.get_for_model(sender)
        Profile.objects.create(content_type=content_type, object_id=kwargs['instance'].pk)
