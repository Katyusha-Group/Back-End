import os
import time

import pandas as pd
import logging

from watchdog.observers import Observer
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
                course_updater.update(data=update_list)
                # group_keys = modifications.all().index.values.tolist()
                # for key in group_keys:
                #     print(key)
                #     print(modifications.get_group([key]))
                # changes = {}
                # changes_count = len(diff) // 2
                # old_data = diff[:changes_count]
                # new_data = diff[changes_count:]
                # indexes = old_data.index.values.tolist()[:changes_count]
                # with pd.option_context('display.max_rows', None, 'display.max_columns',
                #                        None):  # more options can be specified also
                #     print(diff)
                # self.logger.info(f'The following rows have been modified in {self.file}:')
                # for i in range(changes_count):
                #
                #     temp_df = pd.DataFrame(data=old_data.iloc[i]).compare(pd.DataFrame(new_data.iloc[i]),
                #                                                           keep_shape=False)
                #     changes[i] = []
                #     self.logger.info(f'\tIndex {indexes[i]}:')
                #     columns = temp_df.index.values.tolist()
                #     # golestan_updater = GolestanUpdater(old_row=old_data.loc[indexes[i]],
                #     #                                    new_row=new_data.loc[indexes[i]],
                #     #                                    columns=columns)
                #     for col in columns:
                #         old_value = old_data.loc[indexes[i], col]
                #         new_value = new_data.loc[indexes[i], col]
                #         element = {col: (old_value, new_value)}
                #         self.logger.info(f'\t\tColumn: {col} - old value: {old_value}, new value: {new_value}')
                #         changes[i].append(element)
                # Update the DataFrame
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
        create_list = pd.concat(create_list) if len(create_list) > 0 else None
        update_list = pd.concat(update_list) if len(update_list) > 0 else None
        return create_list, update_list
