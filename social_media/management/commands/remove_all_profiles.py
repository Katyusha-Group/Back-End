import time

from django.contrib.auth import get_user_model
from django.contrib.contenttypes.models import ContentType
from django.core.management.base import BaseCommand

from social_media.models import Profile
from university.models import Teacher, BaseCourse


class Command(BaseCommand):
    help = "Delete all profiles from."

    def handle(self, *args, **options):
        pre = time.time()

        Profile.objects.all().delete()

        print("remove_all_profiles --- Time took: ", time.time() - pre)
