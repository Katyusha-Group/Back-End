from django.contrib.auth import get_user_model
from django.db.models import Case, When, Value, BooleanField
from django.db.models.signals import post_save, pre_delete, m2m_changed
from django.dispatch import receiver

from university.models import Course, ExamTimePlace, CourseTimePlace, AllowedDepartment
from custom_config.models import FieldTracker, ModelTracker, WebNotification, OrderItem, Order
import custom_config.scripts.signals_scripts as requirements
from university.scripts import get_or_create
from university.signals import course_teachers_changed
from utils import project_variables


@receiver(post_save, sender=Course)
def create_c_log(sender, **kwargs):
    if kwargs['created']:
        is_course, course_name, course_number, course_pk = requirements.get_course_info(kwargs['instance'])
        requirements.create_model_tracker(is_course, course_name, course_number, 'C', course_pk)


@receiver(pre_delete, sender=Course)
def create_d_log(sender, **kwargs):
    is_course, course_name, course_number, course_pk = requirements.get_course_info(kwargs['instance'])
    requirements.create_model_tracker(is_course, course_name, course_number, 'D', course_pk)


@receiver(post_save, sender=Course)
def create_u_log(sender, **kwargs):
    if not kwargs['created']:
        if 'update_fields' in kwargs and kwargs['update_fields'] is not None:
            is_course, course_name, course_number, course_pk = requirements.get_course_info(kwargs['instance'])
            tracker = requirements.create_model_tracker(is_course, course_name, course_number, 'U', course_pk)

            for field in kwargs['update_fields']:

                for tracker_field in tracker.fields.all():
                    if field == tracker_field.field:
                        tracker_field.delete()

                if field == 'sex':
                    value = project_variables.SEX_EN_TO_FA[kwargs['instance'].__dict__[field]]
                elif field == 'capacity' or field == 'registered_count' or field == 'waiting_count':
                    value = int(float(kwargs['instance'].__dict__[field]))
                else:
                    value = kwargs['instance'].__dict__[field]

                FieldTracker.objects.create(
                    field=field,
                    value=value,
                    tracker=tracker,
                )


@receiver(post_save, sender=ExamTimePlace)
@receiver(post_save, sender=CourseTimePlace)
@receiver(post_save, sender=AllowedDepartment)
def create_u_log_for_course_related(sender, **kwargs):
    if kwargs['created']:
        field = ''

        if kwargs['instance'].__class__.__name__ == 'AllowedDepartment':
            field = 'allowed_departments'
        elif kwargs['instance'].__class__.__name__ == 'ExamTimePlace':
            field = 'exam_time_place'
        elif kwargs['instance'].__class__.__name__ == 'CourseTimePlace':
            field = 'course_time_place'

        is_course, course_name, course_number, course_pk = requirements.get_course_info(kwargs['instance'])
        course = Course.objects.filter(pk=course_pk).first()
        if course is None:
            return

        tracker = requirements.create_model_tracker(is_course, course_name, course_number, 'U', course_pk, field)

        WebNotification.objects.filter(tracker=tracker).delete()

        value = ''

        for tracker_field in tracker.fields.all().reverse():
            if field != 'exam_time_place':
                if field == tracker_field.field:
                    if field == 'course_time_place' and course.base_course.total_unit == 3:
                        value += tracker_field.value.split('،')[-1].strip() + '، '
                else:
                    value += tracker_field.value.split('،')[-1].strip() + '، '
            tracker_field.delete()
            break

        value += kwargs['instance'].__str__()

        FieldTracker.objects.create(
            field=field,
            value=value,
            tracker=tracker,
        )


@receiver(course_teachers_changed, sender=Course)
def teachers_changed(sender, **kwargs):
    is_course, course_name, course_number, course_pk = requirements.get_course_info(kwargs['course'])
    tracker = requirements.create_model_tracker(is_course, course_name, course_number, 'U', course_pk)
    for tracker_field in tracker.fields.all():
        if tracker_field.field == 'teachers':
            tracker_field.delete()
    teacher_names = list(kwargs['course'].teachers.all().values_list('name', flat=True))
    teacher_names = '-'.join(teacher_names)
    FieldTracker.objects.create(
        field='teachers',
        value=teacher_names,
        tracker=tracker,
    )


@receiver(post_save, sender=ModelTracker)
def notification_handler(sender, **kwargs):
    if kwargs['created']:
        model_tracker = kwargs['instance']
        title = ''
        text = ''
        if model_tracker.action == ModelTracker.ACTION_CREATED:
            title = 'ایجاد درس جدید'
            text = 'درس {} با شماره {} ایجاد شد.'.format(model_tracker.course_name, model_tracker.course_number)
        elif model_tracker.action == ModelTracker.ACTION_DELETED:
            title = 'حذف درس'
            text = 'درس {} با شماره {} حذف شد.'.format(model_tracker.course_name, model_tracker.course_number)
        else:
            return
        requirements.create_notification(title, text, model_tracker)


@receiver(post_save, sender=FieldTracker)
def notification_update_handler(sender, **kwargs):
    if kwargs['created']:
        field_tracker = kwargs['instance']
        title = 'ویرایش درس'
        text = 'درس {} با شماره {} ویرایش شد:'.format(field_tracker.tracker.course_name,
                                                      field_tracker.tracker.course_number)
        text += '\n'
        text += '{}: {}'.format(project_variables.course_field_mapper_en_to_fa_notification[field_tracker.field],
                                field_tracker.value)
        requirements.create_notification(title, text, field_tracker.tracker)
