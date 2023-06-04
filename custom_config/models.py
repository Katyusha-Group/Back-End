from uuid import uuid4

from django.conf import settings
from django.core.validators import MinValueValidator, MaxValueValidator
from django.db import models

from university.models import Course, Teacher, AllowedDepartment, CourseTimePlace, ExamTimePlace


class ModelTracker(models.Model):
    ACTION_CHOICES = (
        ('C', 'ایجاد'),
        ('U', 'بروزرسانی'),
        ('D', 'حذف'),
    )

    STATUS_CHOICES = (
        ('U', 'اعمال نشده'),
        ('C', 'اعمال شده'),
    )

    model = models.CharField(max_length=255, verbose_name='مدل')
    instance_id = models.IntegerField(verbose_name='شناسه')
    action = models.CharField(max_length=1, choices=ACTION_CHOICES, verbose_name='عملیات')
    status = models.CharField(max_length=1, choices=STATUS_CHOICES, verbose_name='وضعیت')
    is_course = models.BooleanField(default=False, blank=True, verbose_name='درس است؟')
    course_number = models.CharField(null=True, blank=True, max_length=11, verbose_name='شماره درس')
    course_name = models.CharField(null=True, blank=True, max_length=255, verbose_name='نام درس')
    applied_at = models.DateTimeField(auto_now_add=True, verbose_name='تاریخ ایجاد')

    def __str__(self):
        if self.model == AllowedDepartment.__name__:
            return str(AllowedDepartment.objects.get(pk=self.instance_id))
        if self.model == CourseTimePlace.__name__:
            return str(CourseTimePlace.objects.get(pk=self.instance_id))
        if self.model == ExamTimePlace.__name__:
            return str(ExamTimePlace.objects.get(pk=self.instance_id))

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

    def __str__(self):
        return str(self.id) + ' : ' + str(self.created_at)

    class Meta:
        verbose_name = 'سبد خرید'
        verbose_name_plural = 'سبدهای خرید'


class CartItem(models.Model):
    cart = models.ForeignKey(Cart, on_delete=models.CASCADE, related_name='items')
    course = models.ForeignKey(Course, on_delete=models.CASCADE, related_name='cart_items')
    contain_telegram = models.BooleanField(default=False)
    contain_sms = models.BooleanField(default=False)
    contain_email = models.BooleanField(default=False)

    def __str__(self):
        return str(self.cart) + ' : ' + str(self.course)

    class Meta:
        unique_together = [['cart', 'course']]
        verbose_name = 'آیتم سبد خرید'
        verbose_name_plural = 'آیتم های سبد خرید'


class Order(models.Model):
    PAYMENT_STATUS_PENDING = 'P'
    PAYMENT_STATUS_COMPLETE = 'C'
    PAYMENT_STATUS_FAILED = 'F'
    PAYMENT_STATUS_CHOICES = [
        (PAYMENT_STATUS_PENDING, 'در حال پردازش'),
        (PAYMENT_STATUS_COMPLETE, 'موفق'),
        (PAYMENT_STATUS_FAILED, 'ناموفق')
    ]

    placed_at = models.DateTimeField(auto_now_add=True)
    payment_status = models.CharField(
        max_length=1, choices=PAYMENT_STATUS_CHOICES, default=PAYMENT_STATUS_PENDING)
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.PROTECT)

    def __str__(self):
        return str(self.id) + ' : ' + self.payment_status

    class Meta:
        verbose_name = 'سفارش'
        verbose_name_plural = 'آیتم های سفارش'


class OrderItem(models.Model):
    order = models.ForeignKey(Order, on_delete=models.PROTECT, related_name='items')
    course = models.ForeignKey(Course, on_delete=models.PROTECT, related_name='order_items')
    course_code = models.CharField(max_length=10, default='1')
    contain_telegram = models.BooleanField(default=False)
    contain_sms = models.BooleanField(default=False)
    contain_email = models.BooleanField(default=False)
    unit_price = models.DecimalField(max_digits=9, decimal_places=2)

    def __str__(self):
        return str(self.id) + ' : ' + str(self.order.id) + ' : ' + self.course_code

    class Meta:
        verbose_name = 'سفارش'
        verbose_name_plural = 'آیتم های سفارش'


class TeacherReview(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='teacher_reviews')
    teacher = models.ForeignKey(Teacher, on_delete=models.CASCADE, related_name='teacher_review')
    text = models.TextField(null=True, blank=True)


class TeacherVote(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='teacher_votes')
    vote = models.SmallIntegerField(validators=[MinValueValidator(-1), MaxValueValidator(1)], default=0)
    teacher = models.ForeignKey(Teacher, on_delete=models.CASCADE, related_name='teacher_votes')


class ReviewVote(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='reviews_votes')
    vote = models.SmallIntegerField(validators=[MinValueValidator(-1), MaxValueValidator(1)], default=0)
    review = models.ForeignKey(TeacherReview, on_delete=models.CASCADE, related_name='votes')
