from django.contrib.auth import get_user_model
from django.contrib.contenttypes.models import ContentType
from django.db.models.signals import post_save
from django.dispatch import receiver

from social_media.models import Profile
from university.models import Teacher, BaseCourse

UserModel = get_user_model()


@receiver(post_save, sender=[UserModel, BaseCourse, Teacher])
def create_profile(sender, instance, created, **kwargs):
    if created:
        content_type = ContentType.objects.get_for_model(sender)
        Profile.objects.create(content_type=content_type, object_id=instance.pk)
