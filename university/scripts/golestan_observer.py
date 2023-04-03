import pandas as pd
import logging

from watchdog.events import FileSystemEventHandler

from university.scripts import course_updater


class ExcelHandler(FileSystemEventHandler):
    def __init__(self, file):
        self.file = file
        self.logger = logging.getLogger('changes')
        self.logger.setLevel(logging.DEBUG)
        handler = logging.FileHandler('./changes.log', encoding="utf-8")
        handler.setLevel(logging.DEBUG)
        formatter = logging.Formatter('%(asctime)s - %(message)s')
        handler.setFormatter(formatter)
        self.logger.addHandler(handler)
        self.df = pd.read_excel(file)

    def on_modified(self, event):
        if event.is_directory:
            return None
        elif event.event_type == 'modified' and event.src_path.endswith('golestan_courses.xlsx'):
            # Load the Excel file
            df_new = pd.read_excel(self.file)
            # Compare the rows of the DataFrame
            diff = pd.concat([self.df, df_new]).drop_duplicates(keep=False)
            # Check for changes
            if not diff.empty:
                create_list, update_list = self.make_create_update_list(diff)
                course_updater.create(data=create_list)
                course_updater.update(data=update_list)
                self.df = df_new

    @staticmethod
    def make_create_update_list(diff):
        modifications = diff.groupby(['شماره و گروه درس'])
        update_list = []
        create_list = []
        for key in modifications.groups:
            indices = modifications.groups[key].tolist()
            if len(indices) == 2:
                rows = modifications.get_group(key)
                update_list.append(rows)
            elif len(indices) == 1:
                row = modifications.get_group(key)
                create_list.append(row)
        create_list = pd.concat(create_list) if len(create_list) > 0 else pd.DataFrame()
        update_list = pd.concat(update_list) if len(update_list) > 0 else pd.DataFrame()
        return create_list, update_list
