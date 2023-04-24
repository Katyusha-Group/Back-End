import os
import time

import pandas as pd
from pathlib import Path

from django.core.management.base import BaseCommand

from university.scripts import populate_table
from utils import project_variables


class Command(BaseCommand):
    help = "Populates university models' database, with golestan's data and LMS teachers' data."

    def handle(self, *args, **options):
        # get the path of Excel file
        path = Path(os.path.basename(__file__))
        path = Path(path.parent.absolute())
        golestan_excel_path = (
            os.path.join(path, project_variables.DATA_DIRECTORY_NAME, project_variables.GOLESTAN_EXCEL_FILE))
        teachers_excel_path = (
            os.path.join(path, project_variables.DATA_DIRECTORY_NAME, project_variables.TEACHERS_EXCEL_FILE))
        golestan_data = pd.read_excel(golestan_excel_path)
        teachers_data = pd.read_excel(teachers_excel_path)
        # start populating
        pre = time.time()
        populate_table.populate_all_tables(golestan_data, teachers_data)
        print(time.time() - pre)
