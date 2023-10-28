from django.contrib.auth import get_user_model
from django.db.models.signals import post_save
from django.dispatch import receiver

from social_media.models import Profile

UserModel = get_user_model()


@receiver(post_save, sender=UserModel)
def create_profile(sender, **kwargs):
    user = kwargs['instance']
    if kwargs['created']:
        if user.gender == 'M':
            profile = Profile(
                user=user,
                image='images/profile_pics/male_default.png'
            )
        else:
            profile = Profile(
                user=user,
                image='images/profile_pics/female_default.png'
            )
        profile.save()
