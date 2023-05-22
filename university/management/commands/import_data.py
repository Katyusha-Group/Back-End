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

    def add_arguments(self, parser):
        parser.add_argument('file_name', type=str, default=project_variables.GOLESTAN_EXCEL_FILE_NAME,
                            help='Name of excel file.')

    def handle(self, *args, **options):
        golestan_file_name = options['file_name']

        # get the path of Excel file
        path = Path(os.path.basename(__file__))
        path = Path(path.parent.absolute())
        path = os.path.join(path, project_variables.DATA_DIRECTORY_NAME)

        teachers_excel_path = (
            os.path.join(path, project_variables.TEACHERS_EXCEL_FILE))
        teachers_data = pd.read_excel(teachers_excel_path)
        courses_excel_path = (
            os.path.join(path, golestan_file_name)
        )
        golestan_data = pd.read_excel(courses_excel_path)
        golestan_data = extract_limitation_data(golestan_data)
        # start populating
        pre = time.time()
        populate_table.populate_all_tables(golestan_data, teachers_data)
        print(time.time() - pre)
