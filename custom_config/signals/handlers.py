from django.db.models.signals import post_save, post_delete
from django.dispatch import receiver
from university.models import Course, ExamTimePlace, CourseTimePlace, AllowedDepartment
from custom_config.models import ModelTracker, FieldTracker
import custom_config.scripts.signals_requirements as requirements


@receiver(post_save, sender=ExamTimePlace)
@receiver(post_save, sender=CourseTimePlace)
@receiver(post_save, sender=Course)
@receiver(post_save, sender=AllowedDepartment)
def create_c_log(sender, **kwargs):
    if kwargs['created']:
        is_course, course_name, course_number = requirements.get_course_info(kwargs['instance'])
        requirements.create_model_tracker(is_course, course_name, course_number, 'C', kwargs['instance'])


@receiver(post_delete, sender=Course)
def create_d_log(sender, **kwargs):
    is_course, course_name, course_number = requirements.get_course_info(kwargs['instance'])
    requirements.create_model_tracker(is_course, course_name, course_number, 'U', kwargs['instance'])


@receiver(post_save, sender=Course)
def create_u_log(sender, **kwargs):
    if not kwargs['created']:
        is_course, course_name, course_number = requirements.get_course_info(kwargs['instance'])
        tracker = requirements.create_model_tracker(is_course, course_name, course_number, 'U', kwargs['instance'])

        if 'update_fields' in kwargs and kwargs['update_fields'] is not None:
            fields_list = []

            for field in kwargs['update_fields']:
                if field == 'teacher':
                    field = 'teacher_id'
                fields_list.append(FieldTracker(
                    field=field,
                    value=kwargs['instance'].__dict__[field],
                    tracker=tracker,
                ))

            FieldTracker.objects.bulk_create(fields_list)
