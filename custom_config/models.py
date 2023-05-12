from uuid import uuid4

from django.conf import settings
from django.db import models

from university.models import Course


class ModelTracker(models.Model):
    ACTION_CHOICES = (
        ('C', 'ایجاد'),
        ('U', 'بروزرسانی'),
    )

    STATUS_CHOICES = (
        ('U', 'اعمال نشده'),
        ('C', 'اعمال شده'),
    )

    model = models.CharField(max_length=255, verbose_name='مدل')
    instance_id = models.IntegerField(verbose_name='شناسه')
    action = models.CharField(max_length=1, choices=ACTION_CHOICES, verbose_name='عملیات')
    status = models.CharField(max_length=1, choices=STATUS_CHOICES, verbose_name='وضعیت')
    applied_at = models.DateTimeField(auto_now_add=True, verbose_name='تاریخ ایجاد')

    def __str__(self):
        return str(self.model) + str(self.instance_id) + ' : ' + str(self.action)

    class Meta:
        ordering = ['-applied_at']
        verbose_name = 'ترکر'
        verbose_name_plural = 'ترکرها'


class FieldTracker(models.Model):
    field = models.CharField(max_length=255, verbose_name='ستون')
    value = models.CharField(max_length=1023, verbose_name='مقدار')
    tracker = models.ForeignKey(ModelTracker, on_delete=models.CASCADE, verbose_name='ترکر', related_name='fields')

    def __str__(self):
        return str(self.field) + ' : ' + str(self.value)

    class Meta:
        verbose_name = 'تغییرات ستون'
        verbose_name_plural = 'تغییر ستون ها'


class Cart(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid4)
    created_at = models.DateTimeField(auto_now_add=True)


class CartItem(models.Model):
    cart = models.ForeignKey(Cart, on_delete=models.CASCADE, related_name='items')
    course = models.ForeignKey(Course, on_delete=models.CASCADE)
    contain_telegram = models.BooleanField(default=False)
    contain_sms = models.BooleanField(default=False)
    contain_email = models.BooleanField(default=False)

    class Meta:
        unique_together = [['cart', 'course']]


