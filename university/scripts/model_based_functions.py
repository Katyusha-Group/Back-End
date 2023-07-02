from core.settings import AUTH_USER_MODEL
from university.models import Course


def get_is_allowed(obj: Course, user: AUTH_USER_MODEL):
    return obj.allowed_departments.filter(department__department_number=user.department.department_number).exists()


def get_complete_course_number(obj: Course):
    return str(obj.base_course.course_number) + '_' + str(obj.class_gp)


def get_color_intensity_percentage(obj: Course):
    '''
    Color intensity percentage = ((Remaining capacity - Number of people on the waiting list) / (Total capacity + Number of people on the waiting list + (1.2 * Number of people who want to take the course))) * 100
    '''
    if obj.capacity == 0:
        return 100

    color_intensity_percentage = (((obj.capacity - obj.registered_count) * 100) / (obj.capacity))

    if color_intensity_percentage <= 0:
        return 0
    return (color_intensity_percentage // 10) * 10 + 10 if color_intensity_percentage < 95 else 100
