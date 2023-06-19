from django.db import models
from django.contrib.auth.models import AbstractUser
from university.models import Department


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


class Wallet(models.Model):
    user = models.OneToOneField(to=User, on_delete=models.CASCADE)
    balance = models.DecimalField(max_digits=10, decimal_places=0, default=20000)

    def __str__(self):
        return self.user.email

    def modify_balance(self, amount):
        self.balance -= amount
        self.save()
