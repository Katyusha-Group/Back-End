import time

from django.core.management.base import BaseCommand

from custom_config.notification_requirements import send_notification_for_courses, send_notification_for_course_related


class Command(BaseCommand):
    help = 'Test for notification system'

    def handle(self, *args, **options):
        pre = time.time()

        send_notification_for_courses()
        send_notification_for_course_related()

        print(time.time() - pre)
