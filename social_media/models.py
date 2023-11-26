from django.contrib.auth import get_user_model
from django.core.validators import MinLengthValidator, MaxLengthValidator
from django.db import models
from django.contrib.contenttypes.models import ContentType
from django.core.exceptions import ValidationError
from django.contrib.contenttypes.fields import GenericForeignKey
from django.utils import timezone

from social_media.managers import TwitteManager
from social_media.querysets import NotificationQuerySet
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
    likes = models.ManyToManyField(Profile, related_name='liked_tweets', blank=True)
    conversation = models.ForeignKey('self', related_name='replies', blank=True, null=True, on_delete=models.CASCADE)
    parent = models.ForeignKey('self', related_name='children', blank=True, null=True, on_delete=models.CASCADE)

    def __str__(self):
        return f'{self.profile} twitted {self.content}'

    def get_parent(self):
        if self.parent:
            return self.parent
        return self

    def get_children(self):
        return self.children.all().order_by('-created_at')

    def get_replies(self):
        return self.replies.all().order_by('-created_at')

    def get_likes(self):
        return self.likes.all()

    def get_likes_count(self):
        return self.likes.count()

    def get_replies_count(self):
        return self.replies.count()

    def get_children_count(self):
        return self.children.count()

    def get_conversation(self):
        return self.conversation

    def is_liked_by(self, profile):
        return self.likes.filter(pk=profile.pk).exists()

    def like(self, profile):
        self.likes.add(profile)

    def unlike(self, profile):
        self.likes.remove(profile)

    objects = TwitteManager()


class Notification(models.Model):
    TYPE_LIKE = 'L'
    TYPE_REPLY = 'R'
    TYPE_FOLLOW = 'F'
    TYPE_MENTION = 'M'
    TYPE_CHOICES = (
        (TYPE_LIKE, 'لایک'),
        (TYPE_REPLY, 'پاسخ'),
        (TYPE_FOLLOW, 'دنبال کردن'),
        (TYPE_MENTION, 'منشن')
    )

    objects = NotificationQuerySet.as_manager()

    recipient = models.ForeignKey(Profile, related_name='notifications', on_delete=models.CASCADE)
    actor = models.ForeignKey(Profile, related_name='triggered_notifications', on_delete=models.CASCADE)
    tweet = models.ForeignKey(Twitte, on_delete=models.CASCADE, blank=True, null=True)
    notification_type = models.CharField(max_length=1, choices=TYPE_CHOICES)
    created_at = models.DateTimeField(auto_now_add=True)
    read = models.BooleanField(default=False)

    def __str__(self):
        return f'{self.recipient} got notification {self.notification_type}'

    def save(self, *args, **kwargs):
        if self.notification_type == self.TYPE_FOLLOW:
            if self.tweet:
                raise ValidationError('Invalid value for tweet')
        else:
            if not self.tweet:
                raise ValidationError('Invalid value for tweet')
        super().save(*args, **kwargs)

    def get_delta_time(self):
        delta = timezone.now() - self.created_at
        if delta.days > 0:
            return f'{delta.days} روز پیش'
        if delta.seconds < 60:
            return f'{delta.seconds} ثانیه پیش'
        if delta.seconds < 3600:
            return f'{delta.seconds // 60} دقیقه پیش'
        return f'{delta.seconds // 3600} ساعت پیش'

    def mark_as_read(self):
        self.read = True
        self.save()
