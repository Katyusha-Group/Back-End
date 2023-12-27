import time

from django.contrib.auth import get_user_model
from django.core.management.base import BaseCommand

from university.models import BaseCourse, Department, Semester, Teacher, CourseStudyingGP


class Command(BaseCommand):
    help = "Delete additional departments."

    def handle(self, *args, **options):
        pre = time.time()
        get_user_model().objects.all().delete()
        print('drop_university_tables --- All users have been deleted!')
        BaseCourse.objects.all().delete()
        print('drop_university_tables --- All base courses have been deleted!')
        Department.objects.all().delete()
        print('drop_university_tables --- All departments have been deleted!')
        Semester.objects.all().delete()
        print('drop_university_tables --- All semesters have been deleted!')
        Teacher.objects.all().delete()
        print('drop_university_tables --- All teachers have been deleted!')
        CourseStudyingGP.objects.all().delete()
        print('drop_university_tables --- All course studying gps been deleted!')
        print(time.time() - pre)
