import pandas as pd

from watchdog.events import FileSystemEventHandler

from university.scripts import course_updater
from utils import project_variables


class ExcelHandler(FileSystemEventHandler):
    def __init__(self, file):
        self.file = file
        self.df = pd.read_excel(file)

    def on_modified(self, event):
        if event.is_directory:
            return None
        elif event.event_type == 'modified' and event.src_path.endswith(project_variables.GOLESTAN_EXCEL_FILE):
            # Load the Excel file
            df_new = pd.read_excel(self.file)
            # Compare the rows of the DataFrame
            diff = pd.concat([self.df, df_new]).drop_duplicates(keep=False)
            # Check for changes
            if not diff.empty:
                create_list, update_list = course_updater.make_create_update_list(diff)
                course_updater.create(data=create_list)
                course_updater.update(data=update_list)
                self.df = df_new
