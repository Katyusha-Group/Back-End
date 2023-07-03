import os
import time

import pandas as pd
from pathlib import Path

from django.core.management.base import BaseCommand

from university.models import Department
from utils import project_variables


class Command(BaseCommand):
    help = "Delete additional departments."

    def handle(self, *args, **options):
        pre = time.time()
        for department_id in project_variables.ADDITIONAL_DEPARTMENTS_ID:
            department = Department.objects.filter(department_number=department_id).first()
            if department:
                department.delete()
        print(time.time() - pre)
