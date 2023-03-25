import datetime
from django.db import models
from django.contrib.auth.models import User, AbstractUser
from django.conf import settings
from django.core.exceptions import ValidationError


class User(AbstractUser):
    email = models.EmailField(unique=True)
    is_email_verified = models.BooleanField(default=False)
    

    GENDER_Male = 'M'
    GENDER_Female = 'F'
    GENDER_CHOICES = [
        (GENDER_Female, 'Female'),
        (GENDER_Male, 'Male'),
    ]
    gender = models.CharField(
        max_length=1, choices=GENDER_CHOICES)

    def __str__(self):
        return self.email
