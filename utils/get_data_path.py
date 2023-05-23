import os
from pathlib import Path

import pandas as pd

from utils import project_variables


def get_teachers_data():
    path = get_path_to_data_directory()
    teachers_excel_path = (os.path.join(path, project_variables.TEACHERS_EXCEL_FILE))
    teachers_data = pd.read_excel(teachers_excel_path)
    return teachers_data


def get_path_to_data_directory():
    path = Path(os.path.basename(__file__))
    path = Path(path.parent.absolute())
    path = os.path.join(path, project_variables.DATA_DIRECTORY_NAME)
    return path
