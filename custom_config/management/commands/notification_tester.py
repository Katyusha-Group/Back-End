import time

from django.core.management.base import BaseCommand

from custom_config.scripts.notification import send_notification_for_courses


class Command(BaseCommand):
    help = 'Test for notification system'

    def handle(self, *args, **options):
        pre = time.time()

        send_notification_for_courses()

        print(time.time() - pre)
