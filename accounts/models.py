from decimal import Decimal

from django.db import models
from django.core.validators import MinLengthValidator, RegexValidator
from django.contrib.auth.models import AbstractUser
from django_jalali.db import models as jmodels

from core import settings
from university.models import Department
from utils import project_variables
from utils.transaction_functions import create_ref_code


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
    count_of_verification_code_sent = models.IntegerField(default=0)

    def __str__(self):
        return self.email


class Profile(models.Model):
    user = models.OneToOneField(to=settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='profile')
    image = models.ImageField(upload_to='images/profile_pics', default='images/profile_pics/default.png')
    telegram_id = models.CharField(max_length=32, null=True, blank=True, validators=[
        RegexValidator(regex=r'^[a-zA-Z0-9_]+$',
                                message='telegram id must be alphanumeric or contain underscores'),
        MinLengthValidator(5, message='telegram id must be at least 5 characters long.')])

    def __str__(self):
        return self.user.email


class Wallet(models.Model):
    user = models.OneToOneField(to=settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    balance = models.DecimalField(max_digits=10, decimal_places=0, default=project_variables.INITIAL_WALLET_BALANCE)

    def __str__(self):
        return self.user.email

    def modify_balance(self, amount):
        self.balance -= amount
        self.save()

    def create_transaction(self, amount: Decimal):
        if amount < 0:
            transaction_type = 'D'
        else:
            transaction_type = 'I'
        transaction_status = 'C'
        wallet_transaction = WalletTransaction.objects.create(transaction_type=transaction_type,
                                                              transaction_status=transaction_status,
                                                              amount=amount,
                                                              user=self.user)
        return wallet_transaction


class WalletTransaction(models.Model):
    TRANSACTION_TYPE_CHOICES = (
        ('D', 'کاهش'),
        ('I', 'افزایش'),
    )

    TRANSACTION_STATUS_CHOICES = (
        ('P', 'در حال پردازش'),
        ('C', 'موفق'),
        ('F', 'ناموفق'),
    )

    objects = jmodels.jManager()

    transaction_type = models.CharField(max_length=1, choices=TRANSACTION_TYPE_CHOICES, verbose_name='نوع تراکنش')
    transaction_status = models.CharField(max_length=1, choices=TRANSACTION_STATUS_CHOICES, verbose_name='وضعیت تراکنش')
    amount = models.DecimalField(max_digits=10, decimal_places=0, verbose_name='مبلغ')
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.PROTECT, related_name='wallet_transactions')
    applied_at = jmodels.jDateTimeField(auto_now_add=True, verbose_name='تاریخ ایجاد')
    ref_code = models.CharField(max_length=20, default=create_ref_code, verbose_name='کد مرجع')

    def __str__(self):
        return str(self.transaction_type) + ' : ' + str(self.transaction_status) + ' : ' + str(self.amount)

    class Meta:
        ordering = ['-applied_at']
        verbose_name = 'تراکنش کیف پول'
        verbose_name_plural = 'تراکنش های کیف پول'

