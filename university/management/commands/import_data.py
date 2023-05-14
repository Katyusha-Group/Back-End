import os
import time

import pandas as pd
from pathlib import Path

from django.core.management.base import BaseCommand

from university.scripts import populate_table
from crawler_scripts.golestan_data_cleaner import extract_limitation_data
from utils import project_variables


class Command(BaseCommand):
    help = "Populates university models' database, with golestan's data and LMS teachers' data."

    def handle(self, *args, **options):
        # get the path of Excel file
        path = Path(os.path.basename(__file__))
        path = Path(path.parent.absolute())
        path = os.path.join(path, project_variables.DATA_DIRECTORY_NAME)
        files = [filename for filename in os.listdir(path) if
                 filename.startswith(project_variables.GOLESTAN_COURSES)]
        teachers_excel_path = (
            os.path.join(path, project_variables.TEACHERS_EXCEL_FILE))
        teachers_data = pd.read_excel(teachers_excel_path)
        for file in files:
            print(file)
            file = os.path.join(path, file)
            golestan_data = pd.read_excel(file)
            golestan_data = extract_limitation_data(golestan_data)
            # start populating
            pre = time.time()
            populate_table.populate_all_tables(golestan_data, teachers_data)
            print(time.time() - pre)
