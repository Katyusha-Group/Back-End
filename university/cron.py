import os
import time
from pathlib import Path

import pandas as pd

from university.scripts import course_updater
from utils import project_variables


def watch_golestan():
    pre = time.time()

    path = Path(os.path.basename(__file__))
    path = Path(path.parent.absolute())
    print(os.path.join(path, 'project'))
    suffix = '_' + str(project_variables.CURRENT_SEMESTER) + '.xlsx'
    old_file_name = project_variables.GOLESTAN_EXCEL_FILE_NAME + suffix
    new_file_name = project_variables.NEW_GOLESTAN_EXCEL_FILE_NAME + suffix
    old_file = os.path.join(path, project_variables.DATA_DIRECTORY_NAME, old_file_name)
    new_file = os.path.join(path, project_variables.DATA_DIRECTORY_NAME, new_file_name)

    df = pd.read_excel(old_file)
    df_new = pd.read_excel(new_file)
    diff = pd.concat([df, df_new]).drop_duplicates(keep=False)
    if not diff.empty:
        create_list, update_list = course_updater.make_create_update_list(diff)
        course_updater.create(data=create_list)
        course_updater.update(data=update_list)
        df = df_new
        df.to_excel(old_file, index=False)
        print('Excel file updated successfully')
    else:
        print('Excel file is up to date')

    post = time.time()
    print('Time elapsed: ' + str(post - pre) + ' seconds')


if __name__ == '__main__':
    watch_golestan()
