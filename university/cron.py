import os
import time
import shutil
from pathlib import Path

import pandas as pd

from crawler_scripts.golestan_crawler import GolestanCrawler
from university.scripts import course_updater, app_variables


def watch_golestan():
    path = Path(os.path.basename(__file__))
    path = Path(path.parent.absolute())
    old_path = os.path.join(path, app_variables.DATA_DIRECTORY_NAME, app_variables.EXCEL_FILE)
    new_path = os.path.join(path, app_variables.DATA_DIRECTORY_NAME, app_variables.NEW_EXCEL_FILE)
    pre_time = time.time()
    # crawling golestan
    crawler = GolestanCrawler()
    is_login = crawler.login()
    if is_login:
        crawler.get_courses()
    else:
        print(f'could not extract data from golestan')

    # comparing old and new data
    df_old = pd.read_excel(old_path)
    df_new = pd.read_excel(new_path)
    diff = pd.concat([df_old, df_new]).drop_duplicates(keep=False)
    if not diff.empty:
        create_list, update_list = course_updater.make_create_update_list(diff)
        course_updater.create(data=create_list)
        course_updater.update(data=update_list)
        shutil.copy2(new_path, old_path)

    print(f'watch_golestan took {time.time() - pre_time} seconds')
