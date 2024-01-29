from django.db.models.signals import post_save, pre_delete
from django.dispatch import receiver

from custom_config.scripts import messages
from social_media.signals import send_notification
from university.models import Course, ExamTimePlace, CourseTimePlace, AllowedDepartment, BaseCourse, Teacher
from custom_config.models import FieldTracker, ModelTracker
from social_media.models import Profile, Twitte, Notification
import custom_config.scripts.signals_scripts as requirements
from university.signals import course_teachers_changed
from utils.variables import project_variables


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

        # WebNotification.objects.filter(tracker=tracker).delete()

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
        course_name, course_number = model_tracker.course_name, model_tracker.course_number
        if model_tracker.action == ModelTracker.ACTION_CREATED:
            course = Course.objects.filter(id=model_tracker.instance_id).first()
            text = messages.get_add_message_text(course=course, model_type='C')
            tweet = Twitte.objects.create_twitte(
                profile=Profile.objects.get(profile_type='C', object_id=course.base_course.course_number),
                content=text)
            send_notification.send(sender=None, notification_type=Notification.TYPE_NEW_POST,
                                   actor=tweet.profile, tweet=tweet)

            text = messages.get_add_message_text(course=course, model_type='T')
            for teacher in course.teachers.all():
                tweet = Twitte.objects.create_twitte(
                    profile=Profile.objects.get(profile_type='T', object_id=teacher.id),
                    content=text)
                send_notification.send(sender=None, notification_type=Notification.TYPE_NEW_POST,
                                       actor=tweet.profile, tweet=tweet)

        elif model_tracker.action == ModelTracker.ACTION_DELETED:
            course_number, class_gp = course_number.split('_')
            text = messages.get_delete_message_text(class_gp, 'C')
            tweet = Twitte.objects.create_twitte(
                profile=Profile.objects.get(profile_type='C', object_id=int(course_number)),
                content=text)
            send_notification.send(sender=None, notification_type=Notification.TYPE_NEW_POST,
                                   actor=tweet.profile, tweet=tweet)
        # requirements.create_notification(title, text, model_tracker)


@receiver(post_save, sender=FieldTracker)
def twitter_message_update_creator(sender, **kwargs):
    if kwargs['created']:
        field_tracker = kwargs['instance']

        new_value = str(field_tracker.value)
        course = Course.objects.filter(id=field_tracker.tracker.instance_id).first()
        if course is None:
            return
        field = project_variables.course_field_mapper_en_to_fa_notification[field_tracker.field]

        title, text = messages.get_email_update_for_ordered_courses(course.base_course.name,
                                                                    course.complete_course_number,
                                                                    field, new_value)
        # requirements.create_notification(title, text, field_tracker.tracker)

        tweet = Twitte.objects.create_twitte(
            profile=Profile.objects.get(profile_type='C', object_id=course.base_course.course_number),
            content=messages.get_update_message_text(course.class_gp, field, new_value))
        send_notification.send(sender=None, notification_type=Notification.TYPE_NEW_POST,
                               actor=tweet.profile, tweet=tweet)
