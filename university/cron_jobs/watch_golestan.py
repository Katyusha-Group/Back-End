import shutil

import pandas as pd

from crawler_scripts.golestan_crawler import GolestanCrawler
from university.scripts import course_updater


def watch_golestan(old_path, new_path):
    # crawling golestan
    crawler = GolestanCrawler()
    is_login = crawler.login()
    if is_login:
        crawler.get_courses()
    else:
        print('Could not extract data')

    # comparing old and new data
    df_old = pd.read_excel(old_path)
    df_new = pd.read_excel(new_path)
    diff = pd.concat([df_old, df_new]).drop_duplicates(keep=False)
    if not diff.empty:
        create_list, update_list = course_updater.make_create_update_list(diff)
        course_updater.create(data=create_list)
        course_updater.update(data=update_list)
        shutil.copy2(new_path, old_path)


watch_golestan('old.xlsx', 'new.xlsx')

