from datetime import datetime
from decimal import Decimal

from django.contrib.contenttypes.fields import GenericRelation
from django.core.validators import MinLengthValidator, MaxLengthValidator
from django.db import models
from django.contrib.auth.models import AbstractUser

from django_jalali.db import models as jmodels

from core import settings
from social_media.models import Profile
from university.models import Department
from utils.variables import project_variables
from utils.transactions.transaction_functions import create_ref_code


class User(AbstractUser):
    GENDER_Male = 'M'
    GENDER_Female = 'F'
    GENDER_CHOICES = [
        (GENDER_Female, 'Female'),
        (GENDER_Male, 'Male'),
    ]

    email = models.EmailField(unique=True)
    username = models.CharField(max_length=20, unique=True,
                                validators=[MinLengthValidator(6), ],
                                error_messages={
                                    'unique': 'نام کاربری تکراری است',
                                    'min_length': 'نام کاربری باید حداقل ۶ کاراکتر باشد',
                                    'max_length': 'نام کاربری باید حداکثر ۲۰ کاراکتر باشد'
                                })
    is_email_verified = models.BooleanField(default=False)
    department = models.ForeignKey(to=Department, on_delete=models.DO_NOTHING)
    gender = models.CharField(max_length=1, choices=GENDER_CHOICES)
    verification_code = models.CharField(max_length=4, null=True, blank=True)
    verification_tries_count = models.IntegerField(default=0)
    last_verification_sent = models.DateTimeField(null=True, blank=True, default=datetime.now)
    has_verification_tries_reset = models.BooleanField(default=False)
    profile = GenericRelation(to=Profile, related_query_name='user')

    def get_default_profile_name(self):
        return self.email.split('@')[0]

    def get_default_profile_username(self):
        return self.get_username()

    def get_default_profile_image(self):
        if self.gender == 'M':
            return 'images/profile_pics/male_default.png'
        else:
            return 'images/profile_pics/female_default.png'

    @property
    def is_uni_email(self):
        return self.email.split('@')[1].endswith('iust.ac.ir')

    def __str__(self):
        return self.email


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
