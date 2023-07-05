from custom_config.models import ModelTracker
from university.models import Course


def create_model_tracker(is_course, course_name, course_number, action, instance):
    courses = ModelTracker.objects.filter(course_number=course_number, status='U', model=Course.__name__)
    if courses.exists():
        return courses.first()
    return ModelTracker.objects.create(
        model=Course.__name__,
        instance_id=instance.id,
        action=action,
        status='U',
        is_course=is_course,
        course_number=course_number,
        course_name=course_name,
    )


def get_course_info(instance):
    is_course = instance.__class__.__name__ == Course.__name__
    if is_course:
        course_number = str(instance.base_course.course_number) + '_' + str(instance.class_gp)
        course_name = instance.base_course.name
    else:
        course_number = str(instance.course.base_course.course_number) + '_' + str(instance.course.class_gp)
        course_name = str(instance.course.base_course.name)
    return True, course_name, course_number
