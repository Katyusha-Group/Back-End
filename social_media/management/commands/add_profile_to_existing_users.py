import time

from django.contrib.auth import get_user_model
from django.core.management.base import BaseCommand

from social_media.models import Profile


class Command(BaseCommand):
    help = "Add profile to existing users."

    def handle(self, *args, **options):
        pre = time.time()

        user_model = get_user_model()

        for user in user_model.objects.all():
            profile, created = Profile.objects.get_or_create(user=user)
            if created:
                if user.gender == 'M':
                    profile.image = 'images/profile_pics/male_default.png'
                else:
                    profile.image = 'images/profile_pics/female_default.png'
                profile.save()
                print(f"Profile created for {user.email}")
        print(time.time() - pre)
