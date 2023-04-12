import os
import time

import pandas as pd
from pathlib import Path

from django.core.management.base import BaseCommand, CommandError

from university.scripts import populate_table, app_variables


class Command(BaseCommand):
    help = 'Populates university models\' database, with golestan\'s data.'

    def handle(self, *args, **options):
        # get the path of Excel file
        path = Path(os.path.basename(__file__))
        path = Path(path.parent.absolute())
        path = os.path.join(path, 'data', app_variables.EXCEL_FILE)
        data = pd.read_excel(path)
        # start populating
        pre = time.time()
        populate_table.populate_all_tables(data)
        print(time.time() - pre)
