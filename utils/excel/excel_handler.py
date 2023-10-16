import glob

import pandas as pd
import os

from utils.Excel import excel_cleaner


class ExcelHandler:
    DIR = "../data/"

    def __init__(self):
        self.create_path()

    def create_path(self):
        if not os.path.exists(self.DIR):
            os.makedirs(self.DIR)

    def create_excel(self, data, file_name):
        df = pd.DataFrame(data[1:], columns=data[0])
        df.to_excel(excel_cleaner.get_path(file_name, self.DIR), header=True, index=False)
        excel_cleaner.replace_arabian_with_persian(file_name=file_name, directory=self.DIR)
        print("create_excel:::Excel file created successfully")

    def delete_excel(self, file_name):
        path = excel_cleaner.get_path(file_name, self.DIR)
        if os.path.exists(path):
            os.remove(path)
            print("delete_excel:::Excel file deleted successfully")
        else:
            print("delete_excel:::The file does not exist")

    def concatenate_excel(self, main_pattern):
        self.delete_excel(main_pattern)
        pattern = os.path.join(self.DIR, main_pattern) + "*.xlsx"
        files = glob.glob(pattern)
        dfs = [pd.read_excel(file) for file in files]
        result = pd.concat(dfs)
        result.to_excel(excel_cleaner.get_path(main_pattern, self.DIR), index=False)
        excel_cleaner.clean_data(main_pattern, self.DIR)
        print("concatenate_excel_excel:::Excel files concatenated successfully")
