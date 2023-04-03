import time

import pandas as pd

from university.models import Course, Teacher, CourseTimePlace, ExamTimePlace
from university.scripts import populate_table, maps, get_or_create, clean_data, delete_from_table


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
    courses, exam_time_df, class_time_df = _extract_courses(columns, data_length, diff, new_data)
    columns = _remove_additional_columns(columns)
    Course.objects.bulk_update(courses, fields=[maps.course_field_mapper[col] for col in columns])
    delete_from_table.delete_from_exam_time(exam_time_df)
    delete_from_table.delete_from_course_time(class_time_df)
    populate_table.populate_exam_time(exam_time_df)
    populate_table.populate_course_class_time(class_time_df)


def _extract_courses(columns, data_length, diff, new_data):
    courses = []
    exam_time_list = []
    class_time_list = []
    for i in range(data_length):
        course_code = new_data.iloc[i].loc['شماره و گروه درس']
        course = get_or_create.get_course(course_code=course_code)
        for col in columns:
            old_val = diff.iloc[i].loc[col].loc['self']
            new_val = diff.iloc[i].loc[col].loc['other']
            if pd.isna(old_val) and pd.isna(new_val):
                continue
            if col == 'زمان و مكان امتحان':
                exam_time_list.append(new_data.iloc[i])
            elif col == 'زمان و مكان ارائه':
                class_time_list.append(new_data.iloc[i])
            else:
                course = _update_column(course=course, column=col, value=new_val)
        courses.append(course)
    class_time_df = pd.concat(class_time_list) if len(class_time_list) > 0 else pd.DataFrame()
    exam_time_df = pd.concat(exam_time_list) if len(exam_time_list) > 0 else pd.DataFrame()
    return courses, exam_time_df, class_time_df


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
