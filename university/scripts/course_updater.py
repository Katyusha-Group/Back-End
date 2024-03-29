import time

import pandas as pd
from pandas import DataFrame

from university.models import Course, Teacher
from university.scripts import populate_table, get_or_create, clean_data, delete_from_table
from university.signals import course_teachers_changed
from utils.variables import project_variables
from utils.get_data_path import get_teachers_data


def is_row_deleted(row: DataFrame) -> bool:
    data = pd.DataFrame(data=row.iloc[:, [0, 5]]).values[0]
    return get_or_create.get_course(course_code=data[1], semester=data[0]) is not None


def make_create_update_list(diff) -> dict:
    modifications = diff.groupby([project_variables.COURSE_ID])
    update_list = []
    create_list = []
    delete_list = []
    for key in modifications.groups:
        indices = modifications.groups[key].tolist()
        if len(indices) == 2:
            rows = modifications.get_group(key)
            update_list.append(rows)
        elif len(indices) == 1:
            row = modifications.get_group(key)
            if is_row_deleted(row):
                delete_list.append(row)
            else:
                create_list.append(row)
    create_list = pd.concat(create_list) if len(create_list) > 0 else pd.DataFrame()
    delete_list = pd.concat(delete_list) if len(delete_list) > 0 else pd.DataFrame()
    update_list = pd.concat(update_list) if len(update_list) > 0 else pd.DataFrame()
    return {'create': create_list, 'delete': delete_list, 'update': update_list}


def create(data: pd.DataFrame):
    if data.empty:
        return
    print('Adding new courses to database.')
    pre = time.time()
    populate_table.populate_all_tables(data, get_teachers_data(),
                                       population_mode=project_variables.POPULATION_COURSE_CREATE)
    print(time.time() - pre)


def delete(data):
    if data.empty:
        return
    print('Deleting removed courses from database.')
    pre = time.time()
    delete_from_table.delete_from_course(data)
    print(time.time() - pre)


def update(data: pd.DataFrame):
    if data.empty:
        return
    print('Updating Courses in database.')
    data_length = len(data) // 2
    old_data = data[::2]
    new_data = data[1::2]
    populate_table.populate_teacher(new_data, get_teachers_data())
    old_data_cleaned = old_data.reset_index(drop=True)
    new_data_cleaned = new_data.reset_index(drop=True)
    diff = old_data_cleaned.compare(new_data_cleaned, keep_shape=True)
    columns = [col[0] for col in diff.columns.values.tolist()[::2]]
    new_exam_times, new_class_times, new_allowed_departments, \
    old_class_times, old_exam_times, old_allowed_departments = _extract_courses(
        columns, data_length,
        diff, new_data)
    delete_from_table.delete_from_course_time(old_class_times)
    delete_from_table.delete_from_exam_time(old_exam_times)
    delete_from_table.delete_from_allowed_departments(old_allowed_departments)
    populate_table.populate_course_class_time(new_class_times, ignore_conflicts=False,
                                              population_mode=project_variables.POPULATION_COURSE_UPDATE)
    populate_table.populate_exam_time(new_exam_times, ignore_conflicts=False,
                                      population_mode=project_variables.POPULATION_COURSE_UPDATE)
    populate_table.populate_allowed_departments(new_allowed_departments, ignore_conflicts=False,
                                                population_mode=project_variables.POPULATION_COURSE_UPDATE)


def _extract_courses(modified_columns, data_length, diff, new_data):
    new_exam_times = []
    new_class_times = []
    new_allowed_departments = []
    old_exam_times = []
    old_class_times = []
    old_allowed_departments = []
    columns = new_data.columns
    for i in range(data_length):
        course_code = new_data.iloc[i].loc[project_variables.COURSE_ID]
        course = get_or_create.get_course(course_code=course_code, semester=project_variables.CURRENT_SEMESTER)
        row = new_data.iloc[i].tolist()
        for col in modified_columns:
            old_val = diff.iloc[i].loc[col].loc['self']
            new_val = diff.iloc[i].loc[col].loc['other']
            if pd.isna(old_val) and pd.isna(new_val):
                continue
            if col == project_variables.EXAM_TIME_PLACE:
                new_exam_times.append(row)
                for item in course.exam_times.all():
                    old_exam_times.append(item.id)
            elif col == project_variables.COURSE_TIME_PLACE:
                new_class_times.append(row)
                for item in course.course_times.all():
                    old_class_times.append(item.id)
            elif col == project_variables.REGISTRATION_LIMIT:
                new_allowed_departments.append(row)
                for item in course.allowed_departments.all():
                    old_allowed_departments.append(item.id)
            else:
                course = _update_column(course=course, column=col, value=new_val)
    class_time_df = pd.DataFrame(new_class_times, columns=columns) if len(
        new_class_times) > 0 else pd.DataFrame()
    exam_time_df = pd.DataFrame(new_exam_times, columns=columns) if len(
        new_exam_times) > 0 else pd.DataFrame()
    allowed_departments_df = pd.DataFrame(new_allowed_departments, columns=columns) if len(
        new_allowed_departments) > 0 else pd.DataFrame()
    return exam_time_df, class_time_df, allowed_departments_df, \
           old_class_times, old_exam_times, old_allowed_departments


def _remove_additional_columns(columns):
    if project_variables.EXAM_TIME_PLACE in columns:
        columns.remove(project_variables.EXAM_TIME_PLACE)
    if project_variables.COURSE_TIME_PLACE in columns:
        columns.remove(project_variables.COURSE_TIME_PLACE)
    return columns


def _update_column(course: Course, column: str, value):
    if column == project_variables.CAPACITY:
        course.capacity = value
        course.save(update_fields=['capacity'])
    elif column == project_variables.REGISTERED_COUNT:
        course.registered_count = value
        course.save(update_fields=['registered_count'])
    elif column == project_variables.WAITING_COUNT:
        course.waiting_count = value
        course.save(update_fields=['waiting_count'])
    elif column == project_variables.SEX:
        if value == project_variables.MAN_FA:
            value = 'M'
        elif value == project_variables.WOMAN_FA:
            value = 'F'
        else:
            value = 'B'
        course.sex = value
        course.save(update_fields=['sex'])
    elif column == project_variables.TEACHER:
        names = value.split('-')
        course.teachers.clear()
        for name in names:
            teacher = Teacher.objects.get(name=name)
            course.teachers.add(teacher)
        course.save()
        course_teachers_changed.send_robust(sender=Course, course=course)
    elif column == project_variables.REGISTRATION_LIMIT:
        course.registration_limit = value
        course.save(update_fields=['registration_limit'])
    elif column == project_variables.PRESENTATION_TYPE:
        course.presentation_type = clean_data.determine_presentation_type(value)
        course.save(update_fields=['presentation_type'])
    elif column == project_variables.GUEST_ABLE:
        course.guest_able = clean_data.determine_true_false(value)
        course.save(update_fields=['guest_able'])
    elif column == project_variables.DESCRIPTION:
        course.description = value
        course.save(update_fields=['description'])
    return course
