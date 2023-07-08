import time

from django.core.management.base import BaseCommand

from custom_config.scripts.golestan import watch_golestan
from custom_config.scripts.notification import send_notification_for_courses


class Command(BaseCommand):
    help = 'Watch golestan and send notifications.'

    def handle(self, *args, **options):
        pre = time.time()

        watch_golestan()
        print('Completed watching golestan in', time.time() - pre)

        post = time.time()
        send_notification_for_courses()

        print('Completed sending notification in', time.time() - post)

        print('Total time:', time.time() - pre)
