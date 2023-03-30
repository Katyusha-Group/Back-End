import time

import pandas as pd
import logging

from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler


class ExcelHandler(FileSystemEventHandler):
    def __init__(self, file):
        self.logger = logging.getLogger('changes')
        self.logger.setLevel(logging.DEBUG)
        handler = logging.FileHandler('../../crawler_scripts/changes.log', encoding="utf-8")
        handler.setLevel(logging.DEBUG)
        formatter = logging.Formatter('%(asctime)s - %(message)s')
        handler.setFormatter(formatter)
        self.logger.addHandler(handler)
        self.file = file
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
                changes = {}
                total_changes = len(diff) // 2
                old_data = diff[:total_changes]
                new_data = diff[total_changes:]
                indexes = old_data.index.values.tolist()[:total_changes]
                self.logger.info(f'The following rows have been modified in {self.file}:')
                for i in range(total_changes):
                    temp_df = pd.DataFrame(data=old_data.iloc[i]).compare(pd.DataFrame(new_data.iloc[i]),
                                                                          keep_shape=False)
                    changes[i] = []
                    self.logger.info(f'\tIndex {indexes[i]}:')
                    columns = temp_df.index.values.tolist()
                    for col in columns:
                        old_value = old_data.loc[indexes[i], col]
                        new_value = new_data.loc[indexes[i], col]
                        element = {col: (old_value, new_value)}
                        self.logger.info(f'\t\tColumn: {col} - old value: {old_value}, new value: {new_value}')
                        changes[i].append(element)
                # Update the DataFrame
                self.df = df_new


if __name__ == "__main__":
    event_handler = ExcelHandler('../../data/golestan_courses.xlsx')
    observer = Observer()
    observer.schedule(event_handler,
                      path='../../data/')
    observer.start()
    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        observer.stop()
    observer.join()
