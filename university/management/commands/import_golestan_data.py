import os

import pandas as pd
from pathlib import Path

from django.core.management.base import BaseCommand, CommandError
from django.db import IntegrityError

from university.models import Semester, Department, CourseStudyingGP, BaseCourse, Teacher, ExamTimePlace, \
    CourseTimePlace, Course
from university.scripts import clean_data, get_or_create


class Command(BaseCommand):
    help = 'Populates university models\' database, with golestan\'s data.'

    def handle(self, *args, **options):
        path = Path('import_golestan_data.py')
        path = Path(path.parent.absolute())
        path = os.path.join(path, 'data', 'golestan_courses.xlsx')
        data = pd.read_excel(path)
        self.populate_semester(data)
        self.populate_department(data)
        self.populate_gp_studying(data)
        self.populate_base_course(data)
        self.populate_course(data)

    @staticmethod
    def populate_semester(data: pd.DataFrame):
        try:
            years = data['ترم ارائه درس'].unique()
            Semester.objects.bulk_create([Semester(year=y) for y in years])
        except Exception as ex:
            raise CommandError(ex)

    @staticmethod
    def populate_department(data: pd.DataFrame):
        try:
            df = pd.DataFrame(data=data, columns=['کد دانشكده درس', 'دانشكده درس'])
            departments = df.groupby(['کد دانشكده درس', 'دانشكده درس']).all().index.values
            Department.objects.bulk_create(
                [Department(department_number=dp_id, name=dp_name) for dp_id, dp_name in departments]
            )
        except Exception as ex:
            raise CommandError(ex)

    @staticmethod
    def populate_gp_studying(data: pd.DataFrame):
        try:
            df = pd.DataFrame(data=data, columns=['کد گروه آموزشی درس', 'گروه آموزشي درس'])
            gp_studying = df.groupby(['کد گروه آموزشی درس', 'گروه آموزشي درس']).all().index.values
            CourseStudyingGP.objects.bulk_create(
                [CourseStudyingGP(gp_id=data_gp_id, name=data_gp_name) for data_gp_id, data_gp_name in gp_studying]
            )
        except Exception as ex:
            raise CommandError(ex)

    @staticmethod
    def populate_base_course(data: pd.DataFrame):
        df = pd.DataFrame(data=data.iloc[:, [0, 1, 4, 5, 6, 7, 8, 21]])
        for row in df.values:
            semester = Semester.objects.get(year=row[0])
            department = Department.objects.get(department_number=row[1])
            gp_studying = CourseStudyingGP.objects.get(name=row[2])
            course_number = row[3].split('_')[0]
            try:
                BaseCourse.objects.create(course_number=course_number,
                                          course_studying_gp=gp_studying,
                                          semester=semester,
                                          department=department,
                                          name=row[4],
                                          total_unit=row[5],
                                          practical_unit=row[6],
                                          emergency_deletion=True if row[7] == 'بله' else False)
            except IntegrityError:
                pass
            except Exception as ex:
                print(course_number)
                raise CommandError(ex)

    @staticmethod
    def populate_course(data: pd.DataFrame):
        df = pd.DataFrame(data=data.iloc[:, [5, 9, 10, 11, 12, 13, 14, 15, 19, 22, 23, 16]])
        for row in df.values:
            course_number, course_gp = clean_data.get_course_code(entry=row[0])
            base_course = BaseCourse.objects.get(course_number=course_number)
            teacher = get_or_create.get_or_create_teacher(name=row[5])[0]
            sex = clean_data.determine_sex(sex=row[4])
            presentation_type = clean_data.determine_presentation_type(presentation_type=row[8])
            guest_able = clean_data.determine_guest_able(entry=row[9])
            course = Course.objects.create(class_gp=course_gp, teacher=teacher, base_course=base_course,
                                           sex=sex, presentation_type=presentation_type, guest_able=guest_able,
                                           capacity=row[1], registered_count=row[2], registration_limit=row[11],
                                           waiting_count=row[3], description=row[10])
            try:
                data = clean_data.prepare_data_for_course_time_place(entry=row[6])
                get_or_create.create_course_time_place(course=course, data=data)
            except:
                pass

            try:
                get_or_create.create_exam_time(course=course, entry=row[7])
            except:
                pass
