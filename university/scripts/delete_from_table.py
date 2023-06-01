from university.models import Course, CourseTimePlace, ExamTimePlace, AllowedDepartment
from university.scripts import get_data


def delete_from_course_time(pks):
    if pks:
        db_class_times = CourseTimePlace.objects.filter(id__in=pks)
        db_class_times._raw_delete(db_class_times.db)


def delete_from_exam_time(pks):
    if pks:
        db_exam_times = ExamTimePlace.objects.filter(id__in=pks)
        db_exam_times._raw_delete(db_exam_times.db)


def delete_from_allowed_departments(pks):
    if pks:
        db_allowed_departments = AllowedDepartment.objects.filter(id__in=pks)
        db_allowed_departments._raw_delete(db_allowed_departments.db)
