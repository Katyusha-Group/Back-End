import glob
import sys

import openpyxl
import pandas as pd
import os

from persiantools import characters

from . import project_variables
from django.conf import settings


class ExcelHandler:
    DIR = os.path.join(settings.BASE_DIR, project_variables.DATA_DIRECTORY_NAME)

    def __init__(self):
        self.create_path()

    def get_path(self, file_name):
        return os.path.join(self.DIR, file_name + ".xlsx")

    def create_excel(self, data, file_name):
        df = pd.DataFrame(data[1:], columns=data[0])
        df.to_excel(self.get_path(file_name), header=True, index=False)
        self.replace_arabian_letters_with_persian_letters(file_name=file_name)
        print("Excel file created successfully")

    def concatenate_excel(self, file_name):
        pattern = os.path.join(self.DIR, file_name) + "*.xlsx"
        files = glob.glob(pattern)
        dfs = [pd.read_excel(file) for file in files]
        result = pd.concat(dfs)
        result.to_excel(self.get_path(file_name), index=False)
        print("Excel file created successfully")

    def replace_arabian_letters_with_persian_letters(self, file_name):
        path = self.get_path(file_name)
        workbook = openpyxl.load_workbook(path)
        worksheet = workbook.active
        for row in worksheet.iter_rows():
            for cell in row:
                if cell.value is not None and type(cell.value) == str:
                    cell.value = characters.ar_to_fa(cell.value)
        workbook.save(path)

    @staticmethod
    def make_name_correct(name):
        if 'سيد' in name:
            if 'سيد ' not in name:
                name = name.replace('سيد', 'سيد ')
            parts = name.split()
            name = parts[-2] + ' ' + parts[-1] + ' '.join(parts[:-2])
        else:
            parts = name.split()
            name = parts[-1] + ' ' + ' '.join(parts[:-1])
        return name

    def create_path(self):
        if not os.path.exists(self.DIR):
            os.makedirs(self.DIR)