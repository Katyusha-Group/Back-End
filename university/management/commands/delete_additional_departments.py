import time

from django.core.management.base import BaseCommand
from django.db.models.signals import pre_delete, post_delete

from university.models import Department
from utils.variables import project_variables
from utils.signal.disable_signals import DisableSignals


class Command(BaseCommand):
    help = "Delete additional departments."

    def handle(self, *args, **options):
        pre = time.time()
        for department_id in project_variables.ADDITIONAL_DEPARTMENTS_ID:
            with DisableSignals([pre_delete, post_delete]):
                Department.objects.filter(department_number=department_id).delete()
        print("delete_additional_departments --- Time took:", time.time() - pre)
