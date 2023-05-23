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
        suffix = '_' + str(project_variables.CURRENT_SEMESTER) + '.xlsx'
        old_file_name = project_variables.NEW_GOLESTAN_EXCEL_FILE_NAME + suffix
        new_file_name = project_variables.NEW_GOLESTAN_EXCEL_FILE_NAME + suffix
        old_path = os.path.join(path, project_variables.DATA_DIRECTORY_NAME, old_file_name)
        new_path = os.path.join(path, project_variables.DATA_DIRECTORY_NAME, new_file_name)
        event_handler = ExcelHandler(old_path, new_path)
        observer = Observer()
        observer.schedule(event_handler, path=project_variables.DATA_DIRECTORY)
        observer.start()
        try:
            while True:
                time.sleep(60)
        except KeyboardInterrupt:
            observer.stop()
        observer.join()
