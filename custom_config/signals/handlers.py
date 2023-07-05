from django.db.models.signals import post_save, pre_delete, m2m_changed
from django.dispatch import receiver

from university.models import Course, ExamTimePlace, CourseTimePlace, AllowedDepartment
from custom_config.models import FieldTracker
import custom_config.scripts.signals_requirements as requirements
from university.signals import course_teachers_changed
from utils import project_variables


@receiver(post_save, sender=Course)
def create_c_log(sender, **kwargs):
    if kwargs['created']:
        is_course, course_name, course_number = requirements.get_course_info(kwargs['instance'])
        requirements.create_model_tracker(is_course, course_name, course_number, 'C', kwargs['instance'])


@receiver(pre_delete, sender=Course)
def create_d_log(sender, **kwargs):
    is_course, course_name, course_number = requirements.get_course_info(kwargs['instance'])
    requirements.create_model_tracker(is_course, course_name, course_number, 'D', kwargs['instance'])


@receiver(post_save, sender=Course)
def create_u_log(sender, **kwargs):
    if not kwargs['created']:
        is_course, course_name, course_number = requirements.get_course_info(kwargs['instance'])
        tracker = requirements.create_model_tracker(is_course, course_name, course_number, 'U', kwargs['instance'])

        if 'update_fields' in kwargs and kwargs['update_fields'] is not None:
            fields_list = []

            for field in kwargs['update_fields']:

                for tracker_field in tracker.fields.all():
                    if field == tracker_field.field:
                        tracker_field.delete()
                        break

                if field == 'sex':
                    value = project_variables.SEX_EN_TO_FA[kwargs['instance'].__dict__[field]]
                elif field == 'capacity' or field == 'registered_count' or field == 'waiting_count':
                    value = int(float(kwargs['instance'].__dict__[field]))
                else:
                    value = kwargs['instance'].__dict__[field]

                fields_list.append(FieldTracker(
                    field=field,
                    value=value,
                    tracker=tracker,
                ))

            FieldTracker.objects.bulk_create(fields_list)


@receiver(post_save, sender=ExamTimePlace)
@receiver(post_save, sender=CourseTimePlace)
@receiver(post_save, sender=AllowedDepartment)
def create_u_log_for_course_related(sender, **kwargs):
    if kwargs['created']:
        is_course, course_name, course_number = requirements.get_course_info(kwargs['instance'])
        tracker = requirements.create_model_tracker(is_course, course_name, course_number, 'U', kwargs['instance'])

        field = ''

        if kwargs['instance'].__class__.__name__ == 'AllowedDepartment':
            field = 'allowed_departments'
        elif kwargs['instance'].__class__.__name__ == 'ExamTimePlace':
            field = 'exam_time_place'
        elif kwargs['instance'].__class__.__name__ == 'CourseTimePlace':
            field = 'course_time_place'

        value = ''
        for tracker_field in tracker.fields.all():
            if field == tracker_field.field:
                value += tracker_field.value + '، '
                tracker_field.delete()
        value += kwargs['instance'].__str__()

        FieldTracker.objects.create(
            field=field,
            value=value,
            tracker=tracker,
        )


@receiver(course_teachers_changed, sender=Course)
def teachers_changed(sender, **kwargs):
    is_course, course_name, course_number = requirements.get_course_info(kwargs['course'])
    tracker = requirements.create_model_tracker(is_course, course_name, course_number, 'U', kwargs['course'])
    for tracker_field in tracker.fields.all():
        if tracker_field.field == 'teachers':
            tracker_field.delete()
            break
    teacher_names = list(kwargs['course'].teachers.all().values_list('name', flat=True))
    teacher_names = '-'.join(teacher_names)
    FieldTracker.objects.create(
        field='teachers',
        value=teacher_names,
        tracker=tracker,
    )
