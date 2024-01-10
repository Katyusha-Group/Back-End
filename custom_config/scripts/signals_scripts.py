from django.contrib.auth import get_user_model
from django.db.models import Q

from custom_config.models import ModelTracker, WebNotification, Order
from university.models import Course
from university.scripts import get_or_create
from utils.variables import project_variables


def create_model_tracker(is_course, course_name, course_number, action, pk, field_type=None):
    if field_type:
        trackers = ModelTracker.objects.filter(
            instance_id=pk,
            is_course=is_course,
            status='U',
        ).all()
        for tracker in trackers:
            if tracker.fields.filter(field=field_type).exists():
                return tracker
    return ModelTracker.objects.create(
        model=Course.__name__,
        instance_id=pk,
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
        course_id = instance.id
    else:
        course_number = str(instance.course.base_course.course_number) + '_' + str(instance.course.class_gp)
        course_name = str(instance.course.base_course.name)
        course_id = instance.course.id
    return True, course_name, course_number, course_id


def create_notification(title, text, model_tracker):
    course_number, class_gp = model_tracker.course_number.split('_')

    course = get_or_create.get_course(course_code=model_tracker.course_number,
                                      semester=project_variables.CURRENT_SEMESTER)
    departments = [allowed_department.department for allowed_department in course.allowed_departments.all()]
    users = (
        get_user_model().objects
        .filter(Q(courses=course) | Q(department__in=departments) | Q(department=course.base_course.department)
                | (Q(orders__items__course_number=course_number)
                   & Q(orders__payment_status=Order.PAYMENT_STATUS_COMPLETED)
                   & Q(orders__items__class_gp=class_gp)))
        .distinct()
    )
    notifications = [
        WebNotification(
            title=title,
            text=text,
            user=user,
            tracker=model_tracker,
        )
        for user in users.all()
    ]
    WebNotification.objects.bulk_create(notifications)
