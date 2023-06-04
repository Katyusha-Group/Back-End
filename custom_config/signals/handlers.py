from django.db.models.signals import post_save, post_delete
from django.dispatch import receiver
from university.models import Course, ExamTimePlace, CourseTimePlace, AllowedDepartment
from custom_config.models import ModelTracker, FieldTracker


@receiver(post_save, sender=ExamTimePlace)
@receiver(post_save, sender=CourseTimePlace)
@receiver(post_save, sender=Course)
@receiver(post_save, sender=AllowedDepartment)
def create_c_log(sender, **kwargs):
    if kwargs['created']:
        ModelTracker.objects.create(
            model=kwargs['instance'].__class__.__name__,
            instance_id=kwargs['instance'].id,
            action='C',
            status='U',
        )


@receiver(post_delete, sender=Course)
def create_d_log(sender, **kwargs):
    ModelTracker.objects.create(
        model=kwargs['instance'].__class__.__name__,
        instance_id=kwargs['instance'].id,
        action='D',
        status='U',
    )


@receiver(post_save, sender=Course)
def create_u_log(sender, **kwargs):
    if not kwargs['created']:
        tracker = ModelTracker.objects.create(
            model=kwargs['instance'].__class__.__name__,
            instance_id=kwargs['instance'].id,
            action='U',
            status='U',
        )

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
