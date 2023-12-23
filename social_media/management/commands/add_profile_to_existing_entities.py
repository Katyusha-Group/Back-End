import time

from django.contrib.auth import get_user_model
from django.contrib.contenttypes.models import ContentType
from django.core.management.base import BaseCommand

from social_media.models import Profile
from university.models import Teacher, BaseCourse


class Command(BaseCommand):
    help = "Add profile to existing entities."

    def handle(self, *args, **options):
        if Profile.objects.exists():
            print("add_profile_to_existing_entities --- Profiles already exist.")
            return

        pre = time.time()

        user_model = get_user_model()
        content_user_model = ContentType.objects.get_for_model(user_model)

        for user in user_model.objects.all():
            Profile.objects.create(content_type=content_user_model, object_id=user.pk)
            print(f"add_profile_to_existing_entities --- Profile created for {user.email}")

        content_course_model = ContentType.objects.get_for_model(BaseCourse)
        for course in BaseCourse.objects.all():
            Profile.objects.get_or_create(content_type=content_course_model, object_id=course.pk)
        print(f"add_profile_to_existing_entities --- Profile created for all courses.")

        content_teacher_model = ContentType.objects.get_for_model(Teacher)
        for teacher in Teacher.objects.all():
            Profile.objects.create(content_type=content_teacher_model, object_id=teacher.pk)
        print(f"add_profile_to_existing_entities --- Profile created for all teachers.")

        print("add_profile_to_existing_entities --- Time took:", time.time() - pre)
