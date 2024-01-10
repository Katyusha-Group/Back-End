import pandas as pd

from watchdog.events import FileSystemEventHandler

from university.scripts import course_updater
from utils.variables import project_variables


class ExcelHandler(FileSystemEventHandler):
    def __init__(self, old_file, new_file):
        self.old_file = old_file
        self.new_file = new_file
        self.df = pd.read_excel(old_file)

    def on_modified(self, event):
        if event.is_directory:
            return None
        elif event.event_type == 'modified' and event.src_path.endswith(
                project_variables.NEW_GOLESTAN_EXCEL_FILE_NAME + '_' + str(
                    project_variables.CURRENT_SEMESTER) + '.xlsx'):
            # Load the Excel file
            df_new = pd.read_excel(self.new_file)
            # Compare the rows of the DataFrame
            diff = pd.concat([self.df, df_new]).drop_duplicates(keep=False)
            # Check for changes
            if not diff.empty:
                modification_lists = course_updater.make_create_update_list(diff)
                course_updater.create(data=modification_lists['create'])
                course_updater.update(data=modification_lists['update'])
                course_updater.delete(data=modification_lists['delete'])
                self.df = df_new
                self.df.to_excel(self.old_file, index=False)
                print('Excel file updated successfully')
