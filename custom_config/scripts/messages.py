from social_media.models import Profile
from university.models import Course, Teacher


def get_add_message_text(course: Course, model_type: str):
    if model_type == Profile.TYPE_COURSE:
        return f'گروه درسی جدید با شماره کلاس {course.class_gp} با اساتید زیر به گلستان اضافه شد. \n' \
               f'اساتید: {"، ".join([teacher.name for teacher in course.teachers.all()])} \n'
    elif model_type == Profile.TYPE_TEACHER:
        return f'درس با شماره درس {course.complete_course_number}به گلستان اضافه شد. \n'
    else:
        raise ValueError('Invalid profile type')


def get_delete_message_text(course: Course, model_type: str):
    if model_type == Profile.TYPE_TEACHER:
        return f'درسی با شماره درس {course.complete_course_number}از گلستان حذف شد. \n'
    elif model_type == Profile.TYPE_COURSE:
        return f'گروه درسی با شماره کلاس {course.class_gp}از گلستان حذف شد. \n'
    else:
        raise ValueError('Invalid profile type')


def get_update_message_text(course: Course, field: str, old_value: str, new_value: str):
    return f'گروه درسی با شماره کلاس {course.class_gp} در ستون {field} از مقدار {old_value} به مقدار {new_value} تغییر کرد. \n'

