from django.db import models
from django.conf import settings
from social_media.models import *

class Room(models.Model):
    class Meta:
        app_label = "chat"
        managed = True
    room_name = models.CharField(max_length=250)
    user1 = models.ForeignKey(Profile, related_name='user1', on_delete=models.CASCADE)
    user2 = models.ForeignKey(Profile, related_name='user2', on_delete=models.CASCADE)
    date_created = models.DateTimeField(auto_now_add=True)
    last_updated = models.DateTimeField(auto_now=True)

class Chat(models.Model):
    class Meta:
        app_label = "chat"
        managed = True
    class SenderType(models.TextChoices):
        server = 'SERVER'
        Client = 'CLIENT'
    sender_id = models.ForeignKey(Profile, related_name='send_chats', on_delete=models.CASCADE)
    message = models.TextField()
    date_created = models.DateTimeField(auto_now_add=True)
    room_name = models.CharField(max_length=250)
    sender_type= models.CharField(max_length=6, choices=SenderType.choices,default= 'SERVER', null=True)
    room = models.ForeignKey(Room,related_name="messages",on_delete=models.CASCADE,null= True , default= None)

