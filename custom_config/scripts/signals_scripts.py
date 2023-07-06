from custom_config.models import ModelTracker, Notification, OrderItem, Order
from university.models import Course


def create_model_tracker(is_course, course_name, course_number, action, pk):
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

    order_items = (OrderItem.objects
                   .prefetch_related('order')
                   .filter(course_number=course_number,
                           class_gp=class_gp,
                           order__payment_status=Order.PAYMENT_STATUS_COMPLETED)
                   .all())

    for order_item in order_items:
        notification = Notification.objects.create(
            title=title,
            text=text,
        )
        notification.order_items.add(order_item)
