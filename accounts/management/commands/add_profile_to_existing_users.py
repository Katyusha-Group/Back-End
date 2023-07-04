import time

from django.core.management.base import BaseCommand

from accounts.models import Profile, User
from utils import project_variables


class Command(BaseCommand):
    help = "Add profile to existing users."

    def handle(self, *args, **options):
        pre = time.time()
        for user in User.objects.all():
            profile, created = Profile.objects.get_or_create(user=user)
            if created:
                if user.gender == 'M':
                    profile.image = 'images/profile_pics/male_default.png'
                else:
                    profile.image = 'images/profile_pics/female_default.png'
                profile.save()
                print(f"Profile created for {user.email}")
        print(time.time() - pre)
