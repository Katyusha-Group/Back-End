from django.contrib.auth import get_user_model
from django.contrib.contenttypes.models import ContentType
from django.db.models.signals import post_save
from django.dispatch import receiver

from social_media.models import Profile

UserModel = get_user_model()


@receiver(post_save, sender=UserModel)
def create_profile(sender, **kwargs):
    user = kwargs['instance']
    user_model = ContentType.objects.get_for_model(UserModel)
    if kwargs['created']:
        Profile.objects.create(content_type=user_model, object_id=user.pk)
