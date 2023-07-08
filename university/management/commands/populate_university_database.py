import os
import time

import pandas as pd

from django.core.management.base import BaseCommand

from university.scripts import populate_table
from utils import project_variables
from utils.get_data_path import get_teachers_data, get_path_to_data_directory


class Command(BaseCommand):
    help = "Populates university models' database, with Golestan's data and LMS teachers' data."

    def add_arguments(self, parser):
        parser.add_argument('file_name', type=str, default=project_variables.GOLESTAN_EXCEL_COMPLETE_FILE_NAME,
                            help='Name of excel file.')

    def handle(self, *args, **options):
        golestan_file_name = options['file_name']
        # get the path of Excel file
        teachers_data = get_teachers_data()
        courses_excel_path = (os.path.join(get_path_to_data_directory(), golestan_file_name))
        golestan_data = pd.read_excel(courses_excel_path)
        # start populating
        pre = time.time()
        populate_table.populate_all_tables(golestan_data, teachers_data,
                                           population_mode=project_variables.POPULATION_INITIAL)
        print(time.time() - pre)
