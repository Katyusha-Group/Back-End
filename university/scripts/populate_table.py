import codecs
import os

import pandas as pd
from django.core.files import File
from django.core.management import CommandError
from django.db import transaction

from crawler_scripts.golestan_data_cleaner import extract_limitation_data
from university.models import Semester, Department, CourseStudyingGP, BaseCourse, Teacher, Course, CourseTimePlace, \
    ExamTimePlace, AllowedDepartment
from university.scripts import clean_data, get_data, get_or_create
from utils import project_variables


def populate_all_tables(golestan_data, teachers_data, population_mode=project_variables.POPULATION_INITIAL):
    with transaction.atomic():
        populate_semester(golestan_data)
        populate_department(golestan_data)
        populate_gp_studying(golestan_data)
        populate_base_course(golestan_data)
        populate_teacher(golestan_data, teachers_data)
        populate_course(golestan_data, False, population_mode)
        populate_course_class_time(golestan_data, False, population_mode)
        populate_exam_time(golestan_data, False, population_mode)
        populate_allowed_departments(golestan_data, False, population_mode)


def populate_semester(data, ignore_conflicts=True):
    years = data[project_variables.SEMESTER].unique()
    Semester.objects.bulk_create([Semester(year=y) for y in years],
                                 ignore_conflicts=ignore_conflicts)


def populate_department(data, ignore_conflicts=True):
    columns = [project_variables.DEPARTMENT_ID, project_variables.DEPARTMENT_NAME]
    df = pd.DataFrame(data=data, columns=columns)
    departments = df.groupby(columns).all().index.values
    Department.objects.bulk_create(
        [Department(department_number=dp_id, name=dp_name) for dp_id, dp_name in departments],
        ignore_conflicts=ignore_conflicts
    )


def populate_gp_studying(data, ignore_conflicts=True):
    columns = [project_variables.STUDYING_GROUP_ID, project_variables.STUDYING_GROUP_NAME]
    df = pd.DataFrame(data=data, columns=columns)
    gp_studying = df.groupby(columns).all().index.values
    CourseStudyingGP.objects.bulk_create(
        [CourseStudyingGP(gp_id=data_gp_id, name=data_gp_name) for data_gp_id, data_gp_name in gp_studying],
        ignore_conflicts=ignore_conflicts
    )


def populate_base_course(data, ignore_conflicts=True):
    df = pd.DataFrame(data=data.iloc[:, [1, 4, 5, 6, 7, 8, 21]]).values
    BaseCourse.objects.bulk_create([BaseCourse(department_id=row[0],
                                               course_studying_gp=CourseStudyingGP.objects.get(name=row[1]),
                                               course_number=clean_data.get_course_code(row[2])[0],
                                               emergency_deletion=clean_data.determine_true_false(row[6]),
                                               name=row[3], total_unit=row[4], practical_unit=row[5], )
                                    for row in df],
                                   ignore_conflicts=ignore_conflicts)


def populate_teacher(golestan_data, teachers_data, ignore_conflicts=True):
    df = pd.DataFrame(golestan_data[project_variables.TEACHER].unique())
    names = [name for name in df.iloc[:, 0].values]
    names = pd.DataFrame({'name': names})
    df = pd.merge(names, teachers_data, on='name', how='left').values
    Teacher.objects.bulk_create([Teacher(name=row[0],
                                         golestan_name=row[0],
                                         email_address=row[1],
                                         lms_id=int(row[3]) if not pd.isna(row[3]) else None,
                                         teacher_image_url=row[2],
                                         teacher_lms_image=File(
                                             file=open(f'./data/teachers_images/{int(row[3])}.png',
                                                       'rb'),
                                             name=str(int(row[3])) + '.png') if not pd.isna(
                                             row[3]) and os.path.isfile(
                                             f'./data/teachers_images/{int(row[3])}.png')
                                         else 'images/teachers_image/default.png',
                                         teacher_image=File(
                                             file=open(f'./data/teachers_images/{int(row[3])}.png',
                                                       'rb'),
                                             name=str(int(row[3])) + '.png') if not pd.isna(
                                             row[3]) and os.path.isfile(
                                             f'./data/teachers_images/{int(row[3])}.png')
                                         else 'images/teachers_image/default.png',
                                         )
                                 for row in df],
                                ignore_conflicts=ignore_conflicts)


def populate_course(data, ignore_conflicts=True, population_mode=project_variables.POPULATION_INITIAL):
    df = pd.DataFrame(data.iloc[:, [0, 5, 9, 10, 11, 12, 13, 14, 15, 19, 22, 23, 16]]).values
    if population_mode == project_variables.POPULATION_INITIAL or\
            population_mode == project_variables.POPULATION_COURSE_UPDATE:
        Course.objects.bulk_create(
            [Course(semester_id=row[0],
                    base_course_id=clean_data.get_course_code(entry=row[1])[0],
                    teacher=Teacher.objects.get(name=row[6]),
                    sex=clean_data.determine_sex(sex=row[5]),
                    presentation_type=clean_data.determine_presentation_type(
                        presentation_type=row[9]),
                    guest_able=clean_data.determine_true_false(entry=row[10]),
                    class_gp=clean_data.get_course_code(entry=row[1])[1],
                    capacity=row[2], registered_count=row[3], registration_limit=row[12],
                    waiting_count=row[4], description=row[11])
             for row in df],
            ignore_conflicts=ignore_conflicts)
    else:
        for row in df:
            Course.objects.create(semester_id=row[0],
                                  base_course_id=clean_data.get_course_code(entry=row[1])[0],
                                  teacher=Teacher.objects.get(name=row[6]),
                                  sex=clean_data.determine_sex(sex=row[5]),
                                  presentation_type=clean_data.determine_presentation_type(
                                      presentation_type=row[9]),
                                  guest_able=clean_data.determine_true_false(entry=row[10]),
                                  class_gp=clean_data.get_course_code(entry=row[1])[1],
                                  capacity=row[2], registered_count=row[3], registration_limit=row[12],
                                  waiting_count=row[4], description=row[11])


def populate_course_class_time(data, ignore_conflicts=True, population_mode=project_variables.POPULATION_INITIAL):
    class_times = get_data.get_data_from_course_time(data=data)
    if class_times:
        if population_mode == project_variables.POPULATION_INITIAL or\
                population_mode == project_variables.POPULATION_COURSE_CREATE:
            CourseTimePlace.objects.bulk_create(class_times, ignore_conflicts=ignore_conflicts)
        else:
            for class_time in class_times:
                CourseTimePlace.objects.create(day=class_time.day, start_time=class_time.start_time,
                                               end_time=class_time.end_time, course=class_time.course,
                                               place=class_time.place)


def populate_exam_time(data, ignore_conflicts=True, population_mode=project_variables.POPULATION_INITIAL):
    exams = get_data.get_data_from_exam_time(data=data)
    if exams:
        if population_mode == project_variables.POPULATION_INITIAL or \
                population_mode == project_variables.POPULATION_COURSE_CREATE:
            ExamTimePlace.objects.bulk_create(exams, ignore_conflicts=ignore_conflicts)
        else:
            for exam in exams:
                ExamTimePlace.objects.create(date=exam.date, start_time=exam.start_time,
                                             end_time=exam.end_time, course=exam.course)


def populate_allowed_departments(data, ignore_conflicts=True, population_mode=project_variables.POPULATION_INITIAL):
    data = extract_limitation_data(data)
    allowed_departments = get_data.get_data_from_allowed_departments(data=data)
    if allowed_departments:
        if population_mode == project_variables.POPULATION_INITIAL or \
                population_mode == project_variables.POPULATION_COURSE_CREATE:
            AllowedDepartment.objects.bulk_create(allowed_departments, ignore_conflicts=ignore_conflicts)
        else:
            for allowed_department in allowed_departments:
                AllowedDepartment.objects.create(department=allowed_department.department,
                                                 course=allowed_department.course)
