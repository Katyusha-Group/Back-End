import os
import time

from django.core.management.base import BaseCommand, CommandError
from watchdog.observers import Observer

from university.scripts.golestan_observer import ExcelHandler


class Command(BaseCommand):
    help = 'Start golestan watcher service'

    def handle(self, *args, **options):
        event_handler = ExcelHandler('./data/golestan_courses.xlsx')
        observer = Observer()
        observer.schedule(event_handler,
                          path='./data/')
        observer.start()
        try:
            while True:
                time.sleep(1)
        except KeyboardInterrupt:
            observer.stop()
        observer.join()
