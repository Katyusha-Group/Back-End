import os
import time

import pandas as pd
from pathlib import Path

from django.core.management.base import BaseCommand, CommandError
from django.db import IntegrityError

from university.models import Semester, Department, CourseStudyingGP, BaseCourse, Teacher, ExamTimePlace, \
    CourseTimePlace, Course
from university.scripts import clean_data, get_or_create


class Command(BaseCommand):
    help = 'Populates university models\' database, with golestan\'s data.'

    def __init__(self, stdout=None, stderr=None, no_color=False, force_color=False):
        super().__init__(stdout, stderr, no_color, force_color)
        self.data = None

    def handle(self, *args, **options):
        path = Path('import_golestan_data.py')
        path = Path(path.parent.absolute())
        path = os.path.join(path, 'data', 'golestan_courses.xlsx')
        self.data = pd.read_excel(path)
        pre = time.time()
        self.populate_semester()
        self.populate_department()
        self.populate_gp_studying()
        self.populate_base_course()
        self.populate_teacher()
        self.populate_course()
        self.populate_course_class_time()
        self.populate_exam_time()
        print(time.time() - pre)

    def populate_semester(self):
        try:
            years = self.data['ترم ارائه درس'].unique()
            Semester.objects.bulk_create([Semester(year=y) for y in years])
        except Exception as ex:
            raise CommandError(ex)

    def populate_department(self):
        try:
            df = pd.DataFrame(data=self.data, columns=['کد دانشكده درس', 'دانشكده درس'])
            departments = df.groupby(['کد دانشكده درس', 'دانشكده درس']).all().index.values
            Department.objects.bulk_create(
                [Department(department_number=dp_id, name=dp_name) for dp_id, dp_name in departments]
            )
        except Exception as ex:
            raise CommandError(ex)

    def populate_gp_studying(self):
        try:
            df = pd.DataFrame(data=self.data, columns=['کد گروه آموزشی درس', 'گروه آموزشي درس'])
            gp_studying = df.groupby(['کد گروه آموزشی درس', 'گروه آموزشي درس']).all().index.values
            CourseStudyingGP.objects.bulk_create(
                [CourseStudyingGP(gp_id=data_gp_id, name=data_gp_name) for data_gp_id, data_gp_name in gp_studying]
            )
        except Exception as ex:
            raise CommandError(ex)

    def populate_base_course(self):
        df = pd.DataFrame(data=self.data.iloc[:, [0, 1, 4, 5, 6, 7, 8, 21]]).values
        try:
            BaseCourse.objects.bulk_create([BaseCourse(semester_id=row[0], department_id=row[1],
                                                       course_studying_gp=CourseStudyingGP.objects.get(name=row[2]),
                                                       course_number=clean_data.get_course_code(row[3])[0],
                                                       emergency_deletion=clean_data.determine_true_false(row[7]),
                                                       name=row[4], total_unit=row[5], practical_unit=row[6], )
                                            for row in df], ignore_conflicts=True)
        except Exception as ex:
            raise CommandError(ex)

    def populate_teacher(self):
        try:
            teachers = self.data['نام استاد'].unique()
            Teacher.objects.bulk_create([Teacher(name=name) for name in teachers])
        except Exception as ex:
            raise CommandError(ex)

    def populate_course(self):
        df = pd.DataFrame(data=self.data.iloc[:, [5, 9, 10, 11, 12, 13, 14, 15, 19, 22, 23, 16]]).values
        Course.objects.bulk_create([Course(base_course_id=clean_data.get_course_code(entry=row[0])[0],
                                           teacher=Teacher.objects.get(name=row[5]),
                                           sex=clean_data.determine_sex(sex=row[5]),
                                           presentation_type=clean_data.determine_presentation_type(
                                               presentation_type=row[8]),
                                           guest_able=clean_data.determine_true_false(entry=row[9]),
                                           class_gp=clean_data.get_course_code(entry=row[0])[1],
                                           capacity=row[1], registered_count=row[2], registration_limit=row[11],
                                           waiting_count=row[3], description=row[10])
                                    for row in df])

    def populate_course_class_time(self):
        df = pd.DataFrame(data=self.data, columns=['زمان و مكان ارائه', 'شماره و گروه درس'])
        class_times = []
        for row in df.values:
            course_number, class_gp = clean_data.get_course_code(entry=row[1])
            course = get_or_create.get_course(course_number=course_number, class_gp=class_gp)
            try:
                prep_data = clean_data.prepare_data_for_course_time_place(row[0])
                for pres in prep_data:
                    day, start_time, end_time, place = clean_data.find_presentation_detail(pres.split())
                    class_times.append(CourseTimePlace(day=day, start_time=start_time, end_time=end_time,
                                                       place=place, course=course))
            except:
                pass
        CourseTimePlace.objects.bulk_create(class_times)

    def populate_exam_time(self):
        df = pd.DataFrame(data=self.data, columns=['زمان و مكان امتحان', 'شماره و گروه درس'])
        exams = []
        for row in df.values:
            course_number, class_gp = clean_data.get_course_code(entry=row[1])
            course = get_or_create.get_course(course_number=course_number, class_gp=class_gp)
            try:
                exam_data = row[0].split()
                date = str.join('-', exam_data[1].split('/'))
                exam_start_time, exam_end_time = clean_data.get_time(exam_data[3])
                exams.append(ExamTimePlace(course=course, start_time=exam_start_time,
                                           end_time=exam_end_time, date=date))
            except:
                pass
        ExamTimePlace.objects.bulk_create(exams)
