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

    def __str__(self):
        return self.email


class Verification(models.Model):
    code = models.CharField(max_length=4)
    email = models.EmailField()
    timestamp = models.DateTimeField(default=datetime.datetime.now)

    def send_verification_email(self, token):
        subject = 'Verify your email'

        message = f'Your verification code is {self.code} \n  http://katyushaiust.ir/accounts/activation-confirm/{token}/'
        send_mail(subject='Verify your email', message=message, from_email='asd@asd.asd',
                  recipient_list=[self.email], fail_silently=False)


    def is_valid(self):
        return (timezone.now() - self.timestamp).total_seconds() <= 3600

    def verify_email(self):
        user = User.objects.get(email=self.email)
        user.is_email_verified = True
        user.save()
        self.delete()

    def save(self, *args, **kwargs):
        if not self.code:
            self.code = str(random.randint(1000, 9999))
        super().save(*args, **kwargs)



