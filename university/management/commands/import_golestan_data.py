import os

import pandas as pd
from django.core.management.base import BaseCommand, CommandError
from django.db import IntegrityError
from pathlib import Path

from university.models import Semester, Department, CourseStudyingGP, BaseCourse, Teacher, ExamTimePlace, \
    CourseTimePlace, Course


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
                raise CommandError(ex)

    def populate_course(self, data: pd.DataFrame):
        df = pd.DataFrame(data=data.iloc[:, [5, 9, 10, 11, 12, 13, 14, 15, 19, 22, 23, 16]])
        for row in df.values:
            course_number = row[0].split('_')[0]
            course_gp = row[0].split('_')[1]
            base_course = BaseCourse.objects.get(course_number=course_number)
            teacher = self.get_or_create_teacher(teacher_name=row[5])
            sex = self.determine_sex(row[4])
            presentation_type = self.determine_presentation_type(row[8])
            guest_able = True if row[9] == 'بله' else False
            try:
                course = Course.objects.create(class_gp=course_gp, teacher=teacher, base_course=base_course,
                                               sex=sex, presentation_type=presentation_type, guest_able=guest_able,
                                               capacity=row[1], registered_count=row[2], registration_limit=row[11],
                                               waiting_count=row[3], description=row[10])
            except Exception as ex:
                raise CommandError(ex)
            self.create_course_time_place(course, row[6])
            self.create_exam_time(course, row[7])

    def create_exam_time(self, course, entry):
        try:
            exam_data = entry.split()
            date = str.join('-', exam_data[1].split('/'))
            exam_start_time, exam_end_time = self.get_time(exam_data[3])
            ExamTimePlace.objects.create(course=course, start_time=exam_start_time,
                                         end_time=exam_end_time, date=date)
        except:
            pass

    def create_course_time_place(self, course, entry):
        try:
            presentation_data = entry.split('،')
            for presentation_detail in presentation_data:
                day, start_time, end_time, place = self.find_presentation_detail(presentation_detail.split())
                CourseTimePlace.objects.create(day=day, start_time=start_time, end_time=end_time,
                                               place=place, course=course)
        except:
            pass

    @staticmethod
    def get_or_create_teacher(teacher_name):
        try:
            teacher = Teacher.objects.filter(name=teacher_name).first()
            if not teacher:
                teacher = Teacher.objects.create(name=teacher_name)
        except Exception as ex:
            raise CommandError(ex)
        return teacher

    def find_presentation_detail(self, presentation_detail):
        if presentation_detail[2] == 'شنبه':
            if presentation_detail[1] == 'یک':
                day = 2
            else:
                day = 4
            start_time, end_time = self.get_time(presentation_detail[3])
            place = str.join(' ', presentation_detail[5:])
        else:
            if presentation_detail[1] == 'شنبه':
                day = 1
            elif presentation_detail[1] == 'دوشنبه':
                day = 3
            else:
                day = 5
            start_time, end_time = self.get_time(presentation_detail[2])
            place = str.join(' ', presentation_detail[4:])
        return day, start_time, end_time, place

    @staticmethod
    def get_time(presentation_time_detail):
        presentation_time = presentation_time_detail.split('-')
        return presentation_time[0], presentation_time[1]

    @staticmethod
    def determine_sex(sex):
        if sex == 'مختلط':
            return 'B'
        elif sex == 'مرد':
            return 'M'
        return 'F'

    @staticmethod
    def determine_presentation_type(presentation_type):
        if presentation_type == 'عادي':
            return 'N'
        elif presentation_type == 'الکترونيکي':
            return 'E'
        return 'B'
