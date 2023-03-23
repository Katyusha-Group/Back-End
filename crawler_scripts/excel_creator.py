import pandas as pd
import os


class ExcelCreator:
    DIR = "./data/"
    
    def __init__(self, data, file_name):
        self.data = data
        self.create_path()
        self.path = os.path.join(self.DIR, file_name)

    def create_excel(self):
        df = pd.DataFrame(self.data[1:], columns=self.data[0])
        df.to_excel(self.path, header=True, index=False)
        print("Excel file created successfully")

    def create_path(self):
        if not os.path.exists(self.DIR):
            os.makedirs(self.DIR)
