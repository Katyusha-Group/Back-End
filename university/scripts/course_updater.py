import time

import pandas as pd

from university.models import Course, Teacher
from university.scripts import populate_table, maps, get_or_create, clean_data, delete_from_table
from utils import project_variables


def make_create_update_list(diff):
    modifications = diff.groupby([project_variables.COURSE_ID])
    update_list = []
    create_list = []
    for key in modifications.groups:
        indices = modifications.groups[key].tolist()
        if len(indices) == 2:
            rows = modifications.get_group(key)
            update_list.append(rows)
        elif len(indices) == 1:
            row = modifications.get_group(key)
            create_list.append(row)
    create_list = pd.concat(create_list) if len(create_list) > 0 else pd.DataFrame()
    update_list = pd.concat(update_list) if len(update_list) > 0 else pd.DataFrame()
    return create_list, update_list


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
    print('Updating Courses in database.')
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
        course_code = new_data.iloc[i].loc[project_variables.COURSE_ID]
        course = get_or_create.get_course(course_code=course_code, semester=project_variables.CURRENT_SEMESTER)
        for col in columns:
            old_val = diff.iloc[i].loc[col].loc['self']
            new_val = diff.iloc[i].loc[col].loc['other']
            if pd.isna(old_val) and pd.isna(new_val):
                continue
            if col == project_variables.EXAM_TIME_PLACE:
                exam_time_list.append(new_data.iloc[i])
            elif col == project_variables.COURSE_TIME_PLACE:
                class_time_list.append(new_data.iloc[i])
            else:
                course = _update_column(course=course, column=col, value=new_val)
        courses.append(course)
    class_time_df = pd.concat(class_time_list) if len(class_time_list) > 0 else pd.DataFrame()
    exam_time_df = pd.concat(exam_time_list) if len(exam_time_list) > 0 else pd.DataFrame()
    return courses, exam_time_df, class_time_df


def _remove_additional_columns(columns):
    if project_variables.EXAM_TIME_PLACE in columns:
        columns.remove(project_variables.EXAM_TIME_PLACE)
    if project_variables.COURSE_TIME_PLACE in columns:
        columns.remove(project_variables.COURSE_TIME_PLACE)
    return columns


def _update_column(course: Course, column: str, value):
    if column == project_variables.CAPACITY:
        course.capacity = value
    elif column == project_variables.REGISTERED_COUNT:
        course.registered_count = value
    elif column == project_variables.WAITING_COUNT:
        course.waiting_count = value
    elif column == project_variables.SEX:
        course.sex = value
    elif column == project_variables.TEACHER:
        course.teacher = Teacher.objects.get(name=value)
    elif column == project_variables.REGISTRATION_LIMIT:
        course.registration_limit = value
    elif column == project_variables.PRESENTATION_TYPE:
        course.presentation_type = clean_data.determine_presentation_type(value)
    elif column == project_variables.GUEST_ABLE:
        course.guest_able = clean_data.determine_true_false(value)
    elif column == project_variables.DESCRIPTION:
        course.description = value
    return course
