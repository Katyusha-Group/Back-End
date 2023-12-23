from django.db import models
from django.utils import timezone

from chat.querysets import ChatQuerySet, MessageQuerySet
from core.settings import AUTH_USER_MODEL


class Contact(models.Model):
    user = models.ForeignKey(
        AUTH_USER_MODEL, related_name='friends', on_delete=models.CASCADE)
    friends = models.ManyToManyField('self', blank=True)

    def __str__(self):
        return self.user.username


class Message(models.Model):
    author = models.ForeignKey(
        Contact, related_name='messages', on_delete=models.CASCADE)
    content = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
    is_read = models.BooleanField(default=False)

    objects = MessageQuerySet.as_manager()

    def __str__(self):
        return self.author.user.username

    @property
    def delta_time(self):
        delta = timezone.now() - self.created_at
        if delta.days > 0:
            return f'{delta.days} روز پیش'
        if delta.seconds < 60:
            return f'{delta.seconds} ثانیه پیش'
        if delta.seconds < 3600:
            return f'{delta.seconds // 60} دقیقه پیش'
        return f'{delta.seconds // 3600} ساعت پیش'


class Chat(models.Model):
    participants = models.ManyToManyField(
        Contact, related_name='chats', blank=True)
    messages = models.ManyToManyField(Message, blank=True)

    objects = ChatQuerySet.as_manager()

    def __str__(self):
        return "{}".format(self.pk)
