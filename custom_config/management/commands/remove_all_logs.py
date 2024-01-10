import time

from django.core.management.base import BaseCommand
from custom_config.models import ModelTracker


class Command(BaseCommand):
    help = 'Removing all tracking information from database'

    def handle(self, *args, **options):
        pre = time.time()

        print('Removing all tracking information from database, started... ')

        ModelTracker.objects.all().delete()

        print('Removing all tracking information from database, finished; time taken:', time.time() - pre)
