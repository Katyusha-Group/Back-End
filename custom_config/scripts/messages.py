from social_media.models import Profile
from university.models import Course, Teacher


def get_add_message_text(course: Course, model_type: str):
    if model_type == Profile.TYPE_COURSE:
        return f'گروه درسی جدید با شماره کلاس {course.class_gp} با اساتید زیر به گلستان اضافه شد. \n' \
               f'اساتید: {"، ".join([teacher.name for teacher in course.teachers.all()])} \n'
    elif model_type == Profile.TYPE_TEACHER:
        return f'درس با شماره درس {course.complete_course_number}به گلستان اضافه شد.'
    else:
        raise ValueError('Invalid profile type')


def get_delete_message_text(info: str, model_type: str):
    if model_type == Profile.TYPE_TEACHER:
        return f'درسی با شماره درس {info}از گلستان حذف شد.'
    elif model_type == Profile.TYPE_COURSE:
        return f'گروه درسی با شماره کلاس {info}از گلستان حذف شد.'
    else:
        raise ValueError('Invalid profile type')


def get_update_message_text(class_gp: str, field: str, new_value: str):
    return f'گروه درسی با شماره کلاس {class_gp} در ستون {field} به مقدار {new_value} تغییر کرد.'


def get_email_update_for_ordered_courses(course_name, course_number, field, new_value):
    title = 'ویرایش درس'
    text = 'درس {} با شماره {} ویرایش شد:'.format(course_name, course_number)
    text += '\n'
    text += f'مقدار جدید برای ستون «{field}» ثبت شده است.\n'
    text += 'مقدار جدید: ' + str(new_value)
    return text, title


def get_email_delete_for_ordered_courses(course_name, course_number):
    title = 'حذف درس'
    text = 'درس {} با شماره {} حذف شد.'.format(course_name, course_number)
    return title, text


def get_email_add_for_ordered_courses(course_name, course_number):
    title = 'ایجاد درس جدید'
    text = 'درس {} با شماره {} ایجاد شد.'.format(course_name, course_number)
    return title, text
