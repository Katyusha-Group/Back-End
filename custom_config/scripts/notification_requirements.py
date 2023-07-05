from django.db import transaction
from django.db.models import Q

from custom_config.models import ModelTracker, OrderItem
from university.models import Course
from university.scripts.get_or_create import get_course
from utils import project_variables, email_handler
from utils.project_variables import course_field_mapper_en_to_fa_notification as course_field_mapper


def get_int(s):
    try:
        int(float(s))
    except ValueError:
        return -1, False
    else:
        return int(float(s)), True


def find_untracked_courses():
    return ModelTracker.objects.filter(Q(status='U') & Q(is_course=True)).all()


def find_updated_course_references_completed_orders(course: Course):
    return course.order_items.select_related('order').filter(order__payment_status='C').all()


def find_base_course_references_completed_orders(course: ModelTracker):
    return OrderItem.objects.prefetch_related('order__user').filter(
        Q(order__payment_status='C') & Q(course_number=course.course_number.split('_')[0])).distinct(
        'order__user').all()


def find_reference_course(course_related: ModelTracker) -> Course | None:
    course = get_course(course_code=course_related.course_number, semester=project_variables.CURRENT_SEMESTER)
    return course


def prepare_message_field(field):
    return course_field_mapper[field.field] + ' : ' + field.value + '\n'


def prepare_header_update_message(course, fields):
    message = 'درس با شماره درس ' + str(course.base_course_id) + '_' + course.class_gp + ' و نام ' + \
              course.base_course.name + ' در گلستان ' + project_variables.action_mapper[
                  project_variables.UPDATE] + '.\n'
    message += 'تغییرات به شرح زیر می باشند:\n'
    count = 0
    if fields is not None:
        for field in fields:
            message += prepare_message_field(field)
            count += 1
    if count > 0:
        return message
    else:
        return None


def prepare_header_create_delete_message(course_instance):
    message = 'درس با شماره درس ' + course_instance.course_number + ' و نام ' + \
              course_instance.course_name + ' در گلستان ' + project_variables.action_mapper[
                  course_instance.action] + '.\n'
    return message


def send_notification_to_user(order_item: OrderItem, message: str):
    if order_item.contain_email:
        print('Sending email to: ' + order_item.order.user.email)
        email_handler.send_modification_message(subject='تغییرات جدید',
                                                message=message,
                                                recipient_list=[order_item.order.user.email])
    if order_item.contain_sms:
        print('Sending SMS to: ', order_item.order.user)
        # send_sms(order_item, message)
    if order_item.contain_telegram:
        print('Sending Telegram to: ', order_item.order.user)
        # telegram_notification.send_telegram_notification(user_id=order_item.order.user.id, changes=message)


def send_message_to_all(order_items, message):
    if message is not None or message != '':
        for order_item in order_items:
            send_notification_to_user(order_item=order_item, message=message)


def send_notification_for_courses():
    with transaction.atomic():
        untracked_courses = find_untracked_courses()
        for course_instance in untracked_courses:
            message = None
            if course_instance.action == project_variables.DELETE or course_instance.action == project_variables.CREATE:
                message = (prepare_header_create_delete_message(
                    course_instance=course_instance))
                order_items = find_base_course_references_completed_orders(course_instance)
            elif course_instance.action == project_variables.UPDATE:
                course = Course.objects.filter(id=course_instance.instance_id).first()
                if course:
                    modified_fields = course_instance.fields.all()
                    if not len(modified_fields) == 0:
                        message = prepare_header_update_message(course=course,
                                                                fields=modified_fields)
                        order_items = find_updated_course_references_completed_orders(course)
            send_message_to_all(message=message, order_items=order_items)
            # course_instance.status = project_variables.CREATE
            # course_instance.save()


def append_or_create_dict(course, course_related, pks):
    if course is None:
        print('Course not found for: ', course_related.pk)
        return
    if course.id in pks:
        pks[course.id].append(course_related)
    else:
        pks[course.id] = [course_related]
