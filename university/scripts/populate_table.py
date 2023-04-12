import pandas as pd
from django.core.management import CommandError

from university.models import Semester, Department, CourseStudyingGP, BaseCourse, Teacher, Course, CourseTimePlace, \
    ExamTimePlace
from university.scripts import clean_data, get_data, app_variables


def populate_all_tables(data):
    populate_semester(data)
    populate_department(data)
    populate_gp_studying(data)
    populate_base_course(data)
    populate_teacher(data)
    populate_course(data, False)
    populate_course_class_time(data, False)
    populate_exam_time(data, False)


def populate_semester(data, ignore_conflicts=True):
    try:
        years = data[app_variables.SEMESTER].unique()
        Semester.objects.bulk_create([Semester(year=y) for y in years],
                                     ignore_conflicts=ignore_conflicts)
    except Exception as ex:
        raise CommandError(ex)


def populate_department(data, ignore_conflicts=True):
    columns = [app_variables.DEPARTMENT_ID, app_variables.DEPARTMENT_NAME]
    try:
        df = pd.DataFrame(data=data, columns=columns)
        departments = df.groupby(columns).all().index.values
        Department.objects.bulk_create(
            [Department(department_number=dp_id, name=dp_name) for dp_id, dp_name in departments],
            ignore_conflicts=ignore_conflicts
        )
    except Exception as ex:
        raise CommandError(ex)


def populate_gp_studying(data, ignore_conflicts=True):
    columns = [app_variables.STUDYING_GROUP_ID, app_variables.STUDYING_GROUP_NAME]
    try:
        df = pd.DataFrame(data=data, columns=columns)
        gp_studying = df.groupby(columns).all().index.values
        CourseStudyingGP.objects.bulk_create(
            [CourseStudyingGP(gp_id=data_gp_id, name=data_gp_name) for data_gp_id, data_gp_name in gp_studying],
            ignore_conflicts=ignore_conflicts
        )
    except Exception as ex:
        raise CommandError(ex)


def populate_base_course(data, ignore_conflicts=True):
    df = pd.DataFrame(data=data.iloc[:, [0, 1, 4, 5, 6, 7, 8, 21]]).values
    try:
        BaseCourse.objects.bulk_create([BaseCourse(semester_id=row[0], department_id=row[1],
                                                   course_studying_gp=CourseStudyingGP.objects.get(name=row[2]),
                                                   course_number=clean_data.get_course_code(row[3])[0],
                                                   emergency_deletion=clean_data.determine_true_false(row[7]),
                                                   name=row[4], total_unit=row[5], practical_unit=row[6], )
                                        for row in df],
                                       ignore_conflicts=ignore_conflicts)
    except Exception as ex:
        raise CommandError(ex)


def populate_teacher(data, ignore_conflicts=True):
    try:
        teachers = data[app_variables.TEACHER].unique()
        Teacher.objects.bulk_create([Teacher(name=name) for name in teachers],
                                    ignore_conflicts=ignore_conflicts)
    except Exception as ex:
        raise CommandError(ex)


def populate_course(data, ignore_conflicts=True):
    df = pd.DataFrame(data.iloc[:, [5, 9, 10, 11, 12, 13, 14, 15, 19, 22, 23, 16]]).values
    Course.objects.bulk_create([Course(base_course_id=clean_data.get_course_code(entry=row[0])[0],
                                       teacher=Teacher.objects.get(name=row[5]),
                                       sex=clean_data.determine_sex(sex=row[4]),
                                       presentation_type=clean_data.determine_presentation_type(
                                           presentation_type=row[8]),
                                       guest_able=clean_data.determine_true_false(entry=row[9]),
                                       class_gp=clean_data.get_course_code(entry=row[0])[1],
                                       capacity=row[1], registered_count=row[2], registration_limit=row[11],
                                       waiting_count=row[3], description=row[10])
                                for row in df],
                               ignore_conflicts=ignore_conflicts)


def populate_course_class_time(data, ignore_conflicts=True):
    class_times = get_data.get_data_from_course_time(data=data)
    if class_times:
        CourseTimePlace.objects.bulk_create(class_times, ignore_conflicts=ignore_conflicts)


def populate_exam_time(data, ignore_conflicts=True):
    exams = get_data.get_data_from_exam_time(data=data)
    if exams:
        ExamTimePlace.objects.bulk_create(exams, ignore_conflicts=ignore_conflicts)
