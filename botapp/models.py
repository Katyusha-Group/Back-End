from django.db import models

# Create your models here.


class User_telegram(models.Model):
    hashed_number = models.CharField(max_length=10, blank=True, null=True)
    user_id = models.IntegerField(blank=True, null=True)
    telegram_chat_id = models.CharField(blank=True, null=True, max_length=10)
    telegram_name = models.CharField(blank=True, null=True, max_length=100)
    email = models.EmailField(blank=True, null=True)


    def __str__(self):
        return self.telegram_name