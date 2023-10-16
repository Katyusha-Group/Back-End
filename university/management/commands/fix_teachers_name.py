import time

from django.core.management.base import BaseCommand

from university.models import Teacher
from utils.variables import project_variables


class Command(BaseCommand):
    help = "Fix teachers' name."

    def handle(self, *args, **options):
        pre = time.time()
        for teacher_name in project_variables.TEACHERS_NAME_INCORRECT_TO_CORRECT:
            teacher = Teacher.objects.filter(name__contains=teacher_name).first()
            if teacher:
                teacher.name = project_variables.TEACHERS_NAME_INCORRECT_TO_CORRECT[teacher_name]
                teacher.save()
        for teacher_name in project_variables.TEACHERS_NAME_INCORRECT_SUBSTRING:
            teachers = Teacher.objects.filter(name__contains=teacher_name)
            for teacher in teachers:
                if teacher:
                    parts = teacher.name.split()
                    if parts[0] == teacher_name:
                        new_teacher_name = parts[-1] + ' ' + parts[0] + ' ' + ' '.join(parts[1:-1])
                        teacher.name = new_teacher_name
                        teacher.save()
        for teacher_name in project_variables.ADDITIONAL_TEACHERS_NAME:
            teacher = Teacher.objects.filter(name=teacher_name).first()
            if teacher:
                teacher.delete()
        print(time.time() - pre)
