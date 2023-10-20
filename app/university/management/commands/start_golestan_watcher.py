import os
import time
from pathlib import Path

import pandas as pd
from django.core.management.base import BaseCommand

from university.scripts import course_updater
from utils.variables import project_variables


class Command(BaseCommand):
    help = 'Start golestan watcher service'

    def handle(self, *args, **options):
        pre = time.time()
        path = Path(os.path.basename(__file__))
        path = Path(path.parent.absolute())
        suffix = '_' + str(project_variables.CURRENT_SEMESTER) + '.xlsx'
        old_file_name = project_variables.GOLESTAN_EXCEL_FILE_NAME + suffix
        new_file_name = project_variables.NEW_GOLESTAN_EXCEL_FILE_NAME + suffix
        old_path = os.path.join(path, project_variables.DATA_DIRECTORY_NAME, old_file_name)
        new_path = os.path.join(path, project_variables.DATA_DIRECTORY_NAME, new_file_name)
        df = pd.read_excel(old_path)
        df_new = pd.read_excel(new_path)
        # Compare the rows of the DataFrame
        diff = pd.concat([df, df_new]).drop_duplicates(keep=False)
        # Check for changes
        if not diff.empty:
            modification_lists = course_updater.make_create_update_list(diff)
            course_updater.create(data=modification_lists['create'])
            course_updater.update(data=modification_lists['update'])
            course_updater.delete(data=modification_lists['delete'])
            df_new.to_excel(old_path, index=False)
            print('Excel file updated successfully')
        print('Total time taken for storing differences:', time.time() - pre)
