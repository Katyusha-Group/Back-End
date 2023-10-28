import time

from django.contrib.auth import get_user_model
from django.contrib.contenttypes.models import ContentType
from django.core.management.base import BaseCommand

from social_media.models import Profile


class Command(BaseCommand):
    help = "Add profile to existing users."

    def handle(self, *args, **options):
        pre = time.time()

        user_model = get_user_model()
        content_user_model = ContentType.objects.get_for_model(user_model)

        for user in user_model.objects.all():
            profile, created = Profile.objects.get_or_create(content_type=content_user_model, object_id=user.pk)
            if created:
                print(f"Profile created for {user.email}")
        print(time.time() - pre)
