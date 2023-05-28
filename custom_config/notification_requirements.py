import codecs

from django.db import transaction
from django.db.models import Q, Manager
from django.core.mail import send_mail

from core.settings import EMAIL_HOST
from custom_config.models import ModelTracker, OrderItem
from university.models import Course, AllowedDepartment, CourseTimePlace, ExamTimePlace, Teacher
from utils.project_variables import course_field_mapper_en_to_fa_notification as course_field_mapper


def find_untracked_courses():
    return ModelTracker.objects.filter(Q(status='U') & Q(model=Course.__name__)).all()


def find_untracked_course_related():
    return ModelTracker.objects.filter(Q(status='U') & ~Q(model=Course.__name__)).all()


def find_complete_related_orders(course: Course):
    return course.order_items.filter(order__payment_status='C').all()


def find_related_course(course_related: ModelTracker) -> Course | None:
    if course_related.model == AllowedDepartment.__name__:
        return AllowedDepartment.objects.filter(pk=course_related.instance_id).first().course
    elif course_related.model == CourseTimePlace.__name__:
        return CourseTimePlace.objects.filter(pk=course_related.instance_id).first().course
    elif course_related.model == ExamTimePlace.__name__:
        return ExamTimePlace.objects.filter(pk=course_related.instance_id).first().course
    return None


def related_to_course(course_related: ModelTracker) -> Course | None:
    course = find_related_course(course_related)
    if course is not None:
        return course
    return None


def prepare_message_field(field):
    if field.field == 'teacher_id':
        field.value = Teacher.objects.get(pk=field.value).name
    return course_field_mapper[field.field] + ' : ' + field.value + '\n'


def prepare_related_message_field(field):
    return course_field_mapper[field.model] + ' : ' + str(field) + '\n'


def prepare_header_message(course, related, fields=None):
    message = 'تغییراتی جدید در درس ' + str(course) + ' ثبت شده است.\n'
    message += 'تغییرات به شرح زیر می باشند:\n'
    if fields is not None:
        for field in fields:
            if related:
                message += prepare_related_message_field(field)
            else:
                message += prepare_message_field(field)
    return message


def send_notification_to_user(order_item: OrderItem, message: str):
    if order_item.contain_email:
        print('Sending email to: ' + order_item.order.user.email)
        send_mail(
            recipient_list=[order_item.order.user.email],
            subject='تغییر در واحد های گلستان',
            message=message,
            from_email=EMAIL_HOST
        )
    if order_item.contain_sms:
        print('Sending SMS to: ', order_item.order.user)
        # send_sms(order_item, message)
    if order_item.contain_telegram:
        print('Sending Telegram to: ', order_item.order.user)
        # send_telegram_message(order_item, message)


def prepare_and_send_message(course, fields, order_users, related=False):
    message = prepare_header_message(course, related, fields)
    for order_user in order_users:
        send_notification_to_user(order_user, message)


def send_notification_for_courses():
    with transaction.atomic():
        untracked_courses = find_untracked_courses()
        for course_instance in untracked_courses:
            # course_instance.status = 'C'
            # course_instance.save()
            course = Course.objects.get(id=course_instance.instance_id)
            order_users = find_complete_related_orders(course)
            modified_fields = course_instance.fields.all()
            if len(modified_fields) == 0:
                continue
            prepare_and_send_message(course, modified_fields, order_users)


def send_notification_for_course_related():
    with transaction.atomic():
        untracked_course_related = find_untracked_course_related()
        pks = {}
        for course_related in untracked_course_related:
            # course_related.status = 'C'
            # course_related.save()
            course = related_to_course(course_related)
            append_or_create_dict(course, course_related, pks)
        for pk in pks:
            course_related_list = pks.get(pk)
            course = Course.objects.get(pk=pk)
            order_users = find_complete_related_orders(course)
            prepare_and_send_message(course, course_related_list, order_users, related=True)


def append_or_create_dict(course, course_related, pks):
    if course.id in pks:
        pks[course.id].append(course_related)
    else:
        pks[course.id] = [course_related]
