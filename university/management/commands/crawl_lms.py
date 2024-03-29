from threading import Thread

import time

import pandas as pd
from django.core.management.base import BaseCommand
from crawler_scripts.lms_crawler_multi_thread import get_teachers_info, grab_teacher_photo
from utils.variables import project_variables
from utils.excel.excel_handler import ExcelHandler


class Command(BaseCommand):
    help = 'Crawls golestan and extracts data into a Excel file.'

    def handle(self, *args, **options):
        pre = time.time()

        threads = []

        for i in range(10):
            t = Thread(target=get_teachers_info, args=(i, ))
            t.start()
            threads.append(t)

        for i in range(10):
            threads[i].join()

        count = len(pd.read_excel('./data/teachers_info.xlsx')) // 10 + 1

        for i in range(10):
            t = Thread(target=grab_teacher_photo, args=(i, count))
            t.start()
            threads.append(t)

        for i in range(10):
            threads[i].join()

        ExcelHandler().replace_arabian_with_persian(project_variables.TEACHERS_EXCEL_NAME)
        ExcelHandler().fix_lms_teachers_name()

        print(time.time() - pre)
