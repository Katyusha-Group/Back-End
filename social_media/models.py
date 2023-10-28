from django.contrib.auth import get_user_model
from django.db import models
from django.conf import settings
from django.contrib.contenttypes.models import ContentType
from django.core.exceptions import ValidationError
from django.contrib.contenttypes.fields import GenericForeignKey

from university.models import Course, Teacher
from utils.variables import project_variables


class Profile(models.Model):
    TYPE_TEACHER = 'T'
    TYPE_COURSE = 'C'
    TYPE_USER = 'U'
    TYPE_VERIFIED_USER = 'V'

    ACTION_CHOICES = (
        (TYPE_TEACHER, 'استاد'),
        (TYPE_COURSE, 'درس'),
        (TYPE_USER, 'کاربر'),
        (TYPE_VERIFIED_USER, 'کاربر تاییدشده')
    )

    content_type = models.OneToOneField(ContentType, on_delete=models.CASCADE)
    object_id = models.PositiveIntegerField()
    content_object = GenericForeignKey('content_type', 'object_id')
    name = models.CharField(max_length=100, blank=True, null=True)
    username = models.CharField(max_length=100, blank=True, null=True)
    image = models.ImageField(upload_to='images/profile_pics', default='images/profile_pics/default.png')
    profile_type = models.CharField(max_length=1, choices=ACTION_CHOICES, default=TYPE_USER)

    def __str__(self):
        return self.name

    def save(self, *args, **kwargs):
        user_model = get_user_model()
        if not isinstance(self.content_object, (Course, Teacher, user_model)):
            raise ValidationError('Invalid value for content_object')
        self.name = self.determine_name(self.name)
        self.username = self.determine_username(self.username)
        self.profile_type = self.determine_profile_type()
        self.image = self.determine_image(self.image)
        super().save(*args, **kwargs)

    def determine_image(self, image):
        if not self.pk:
            return self.content_object.get_default_profile_image()
        return image

    def determine_name(self, name):
        if not self.pk:
            return self.content_object.get_default_profile_name()
        return name

    def determine_username(self, username):
        if not self.pk:
            return self.content_object.get_default_profile_username()
        return username

    def determine_profile_type(self):
        if not self.pk:
            user_model = get_user_model()
            if isinstance(self.content_object, user_model):
                return self.TYPE_USER
            if isinstance(self.content_object, Teacher):
                return self.TYPE_TEACHER
            if isinstance(self.content_object, Course):
                return self.TYPE_COURSE
            # TODO: determine profile type for verified users
            return None
        return self.profile_type
