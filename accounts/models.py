import datetime
from django.db import models
from django.contrib.auth.models import AbstractUser
from university.models import Department
from django.core.mail import send_mail
from django.utils import timezone
import secrets
# improt random
import random
from rest_framework_simplejwt.tokens import RefreshToken





class User(AbstractUser):
    GENDER_Male = 'M'
    GENDER_Female = 'F'
    GENDER_CHOICES = [
        (GENDER_Female, 'Female'),
        (GENDER_Male, 'Male'),
    ]

    email = models.EmailField(unique=True)
    is_email_verified = models.BooleanField(default=False)
    department = models.ForeignKey(to=Department, on_delete=models.DO_NOTHING)
    gender = models.CharField(max_length=1, choices=GENDER_CHOICES)
    verification_code = models.CharField(max_length=4, null=True, blank=True)

    def __str__(self):
        return self.email

