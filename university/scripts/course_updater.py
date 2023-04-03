import time

import pandas as pd

from university.models import Course, Teacher, CourseTimePlace, ExamTimePlace
from university.scripts import populate_table, maps, get_or_create, clean_data


def create(data: pd.DataFrame):
    if data.empty:
        return
    print('Adding new courses to database.')
    pre = time.time()
    populate_table.populate_all_tables(data)
    print(time.time() - pre)


def update(data: pd.DataFrame):
    if data.empty:
        return
    data_length = len(data) // 2
    old_data = data[::2]
    new_data = data[1::2]
    populate_table.populate_teacher(new_data)
    diff = old_data.compare(new_data, keep_shape=False)
    columns = [col[0] for col in diff.columns.values.tolist()[::2]]
    courses = _extract_courses(columns, data_length, diff, old_data)
    columns = _remove_additional_columns(columns)
    Course.objects.bulk_update(courses, fields=[maps.course_field_mapper[col] for col in columns])
    _delete_course_time_place(courses)
    _delete_exam_time(courses)
    populate_table.populate_course_class_time(data=new_data)
    populate_table.populate_exam_time(data=new_data)


def _extract_courses(columns, data_length, diff, old_data):
    courses = []
    for i in range(data_length):
        course_code = old_data.iloc[i].loc['شماره و گروه درس']
        course = get_or_create.get_course(course_code=course_code)
        for col in columns:
            old_val = diff.iloc[i].loc[col].loc['self']
            new_val = diff.iloc[i].loc[col].loc['other']
            if pd.isna(old_val) and pd.isna(new_val):
                continue
            course = _update_column(course=course, column=col, value=new_val)
        courses.append(course)
    return courses


def _remove_additional_columns(columns):
    if 'زمان و مكان امتحان' in columns:
        columns.remove('زمان و مكان امتحان')
    if 'زمان و مكان ارائه' in columns:
        columns.remove('زمان و مكان ارائه')
    return columns


def _update_column(course: Course, column: str, value):
    if column == 'ظر فيت':
        course.capacity = value
    elif column == 'ثبت نام شده':
        course.registered_count = value
    elif column == 'تعداد ليست انتظار':
        course.waiting_count = value
    elif column == 'جنس':
        course.sex = value
    elif column == 'نام استاد':
        course.teacher = Teacher.objects.get(name=value)
    elif column == 'محدوديت اخذ':
        course.registration_limit = value
    elif column == 'نحوه ارائه درس':
        course.presentation_type = clean_data.determine_presentation_type(value)
    elif column == 'امكان اخذ توسط مهمان':
        course.guest_able = clean_data.determine_true_false(value)
    elif column == 'توضيحات':
        course.description = value
    return course


def _delete_course_time_place(courses: list[Course]):
    course_time_list = []
    for course in courses:
        for course_time in course.coursetimeplace_set.all():
            course_time_list.append(course_time.id)
    course_time_list_query = CourseTimePlace.objects.filter(pk__in=course_time_list)
    course_time_list_query._raw_delete(using=course_time_list_query.db)


def _delete_exam_time(courses: list[Course]):
    exam_time_list = []
    for course in courses:
        for course_time in course.examtimeplace_set.all():
            exam_time_list.append(course_time.id)
    exam_time_list_query = ExamTimePlace.objects.filter(pk__in=exam_time_list)
    exam_time_list_query._raw_delete(using=exam_time_list_query.db)
