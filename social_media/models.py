from django.contrib.auth import get_user_model
from django.core.validators import MinLengthValidator, MaxLengthValidator
from django.db import models
from django.contrib.contenttypes.models import ContentType
from django.core.exceptions import ValidationError
from django.contrib.contenttypes.fields import GenericForeignKey

from university.models import BaseCourse, Teacher


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

    content_type = models.ForeignKey(ContentType, on_delete=models.CASCADE)
    object_id = models.PositiveIntegerField()
    content_object = GenericForeignKey('content_type', 'object_id')

    name = models.CharField(max_length=50, blank=True, null=True, error_messages={
        'max_length': 'نام باید حداکثر ۵۰ کاراکتر باشد'})
    username = models.CharField(max_length=20, blank=True, null=True, unique=True, validators=[
        MinLengthValidator(6)],
        error_messages={
            'unique': 'نام کاربری تکراری است',
            'min_length': 'نام کاربری باید حداقل ۶ کاراکتر باشد',
            'max_length': 'نام کاربری باید حداکثر ۲۰ کاراکتر باشد'})
    image = models.ImageField(upload_to='images/profile_pics', default='images/profile_pics/default.png')
    profile_type = models.CharField(max_length=1, choices=ACTION_CHOICES, default=TYPE_USER)
    created_at = models.DateTimeField(auto_now_add=True)
    is_private = models.BooleanField(default=False)

    class Meta:
        indexes = [
            models.Index(fields=["content_type", "object_id"]),
            models.Index(fields=["username"]),
        ]
        unique_together = ('content_type', 'object_id')

    def __str__(self):
        return self.name

    def save(self, *args, **kwargs):
        user_model = get_user_model()
        if not isinstance(self.content_object, (BaseCourse, Teacher, user_model)):
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
                if self.content_object.is_uni_email:
                    return self.TYPE_VERIFIED_USER
                return self.TYPE_USER
            if isinstance(self.content_object, Teacher):
                return self.TYPE_TEACHER
            if isinstance(self.content_object, BaseCourse):
                return self.TYPE_COURSE
            return None
        return self.profile_type

    @staticmethod
    def get_profile_for_user(user):
        user_model = get_user_model()
        user_model = ContentType.objects.get_for_model(user_model)
        return Profile.objects.filter(content_type=user_model, object_id=user.pk).first()


class Follow(models.Model):
    follower = models.ForeignKey(Profile, related_name='following', on_delete=models.CASCADE)
    following = models.ForeignKey(Profile, related_name='followers', on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ('follower', 'following')
        indexes = [
            models.Index(fields=["follower", "following"]),
        ]

    def __str__(self):
        return f'{self.follower} follows {self.following}'


class Twitte(models.Model):
    profile = models.ForeignKey(Profile, on_delete=models.CASCADE)
    content = models.TextField(max_length=280, validators=[
        MinLengthValidator(1),
        MaxLengthValidator(280)
    ])
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f'{self.profile} twitted {self.content}'
        
    class Meta:
        indexes = [
            models.Index(fields=["profile"]),
        ]
        
   