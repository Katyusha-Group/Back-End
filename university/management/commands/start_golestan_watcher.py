import os
import time
from pathlib import Path

from django.core.management.base import BaseCommand
from watchdog.observers import Observer

from utils import project_variables
from university.scripts.golestan_observer import ExcelHandler


class Command(BaseCommand):
    help = 'Start golestan watcher service'

    def handle(self, *args, **options):
        path = Path(os.path.basename(__file__))
        path = Path(path.parent.absolute())
        path = os.path.join(path, project_variables.DATA_DIRECTORY_NAME, project_variables.ALL_GOLESTAN_EXCEL_FILE)
        event_handler = ExcelHandler(path)
        observer = Observer()
        observer.schedule(event_handler, path=project_variables.DATA_DIRECTORY)
        observer.start()
        try:
            while True:
                time.sleep(1)
        except KeyboardInterrupt:
            observer.stop()
        observer.join()
