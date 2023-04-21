import glob

import pandas as pd
import os


class ExcelHandler:
    DIR = "../data/"

    def __init__(self):
        self.create_path()

    def get_path(self, file_name):
        return os.path.join(self.DIR, file_name + ".xlsx")

    def create_excel(self, data, file_name):
        df = pd.DataFrame(data[1:], columns=data[0])
        df.to_excel(self.get_path(file_name), header=True, index=False)
        print("Excel file created successfully")

    def concatenate_excel(self, file_name):
        pattern = os.path.join(self.DIR, file_name) + "*.xlsx"
        files = glob.glob(pattern)
        dfs = [pd.read_excel(file) for file in files]
        result = pd.concat(dfs)
        result.to_excel(self.get_path(file_name), index=False)
        print("Excel file created successfully")

    def create_path(self):
        if not os.path.exists(self.DIR):
            os.makedirs(self.DIR)
