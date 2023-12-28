import time

from django.core.management.base import BaseCommand

from custom_config.scripts import messages
from social_media.models import Twitte, Profile

from custom_config.scripts.notification import send_notification_for_courses
from university.models import Course
from utils.variables import project_variables


class Command(BaseCommand):
    help = 'Add initial tweets to database'

    def handle(self, *args, **options):
        pre = time.time()

        print('add_initial_tweets --- Adding initial tweets to database started...')

        # Checking if initial twits already exist in database, if so, do nothing
        if Twitte.objects.filter(profile__profile_type__in=['C', 'T']).exists():
            print('add_initial_tweets --- Initial twits already exist in database; time taken:', time.time() - pre)
            return

        courses = Course.objects.filter(semester=project_variables.CURRENT_SEMESTER).all()
        for course in courses:
            Twitte.objects.create_twitte(
                content=messages.get_add_message_text(course, 'C'),
                profile=Profile.objects.get(profile_type='C', object_id=course.base_course.course_number)
            )
            for teacher in course.teachers.all():
                Twitte.objects.create_twitte(
                    content=messages.get_add_message_text(course, 'T'),
                    profile=Profile.objects.get(profile_type='T', object_id=teacher.pk),
                )

        print('add_initial_tweets --- initial_tweets added; Time taken:', time.time() - pre)
