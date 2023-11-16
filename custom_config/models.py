from uuid import uuid4

from django.conf import settings
from django.core.validators import MinValueValidator, MaxValueValidator
from django.db import models

from university.models import Course, Teacher, AllowedDepartment, CourseTimePlace, ExamTimePlace
from utils.model_functions.date import get_persian_date
from utils.variables import project_variables
from utils.transactions.transaction_functions import create_ref_code


class ModelTracker(models.Model):
    ACTION_CREATED = 'C'
    ACTION_UPDATED = 'U'
    ACTION_DELETED = 'D'

    ACTION_CHOICES = (
        (ACTION_CREATED, 'ایجاد'),
        (ACTION_UPDATED, 'بروزرسانی'),
        (ACTION_DELETED, 'حذف'),
    )

    STATUS_UNCOMMITTED = 'U'
    STATUS_COMMITTED = 'C'

    STATUS_CHOICES = (
        (STATUS_UNCOMMITTED, 'اعمال نشده'),
        (STATUS_COMMITTED, 'اعمال شده'),
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

    def total_price(self):
        total = 0
        for item in self.items.all():
            total += float(item.get_item_price())
        return total * project_variables.TAX + total

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

    def get_item_price(self):
        total_price = 0
        if self.contain_email:
            total_price += project_variables.EMAIL_PRICE
        if self.contain_sms:
            total_price += project_variables.SMS_PRICE
        if self.contain_telegram:
            total_price += project_variables.TELEGRAM_PRICE
        return total_price

    class Meta:
        unique_together = [['cart', 'course']]
        verbose_name = 'آیتم سبد خرید'
        verbose_name_plural = 'آیتم های سبد خرید'


class Order(models.Model):
    PAYMENT_STATUS_PENDING = 'P'
    PAYMENT_STATUS_COMPLETED = 'C'
    PAYMENT_STATUS_FAILED = 'F'
    PAYMENT_STATUS_CHOICES = [
        (PAYMENT_STATUS_PENDING, 'در حال پردازش'),
        (PAYMENT_STATUS_COMPLETED, 'موفق'),
        (PAYMENT_STATUS_FAILED, 'ناموفق')
    ]
    PAY_ONLINE = 'O'
    PAY_WALLET = 'W'
    PAYMENT_METHOD_CHOICES = (
        (PAY_ONLINE, 'پرداخت آنلاین'),
        (PAY_WALLET, 'پرداخت از طریق کیف پول'),
    )

    placed_at = models.DateTimeField(auto_now_add=True)
    payment_status = models.CharField(
        max_length=1, choices=PAYMENT_STATUS_CHOICES, default=PAYMENT_STATUS_PENDING
    )
    payment_method = models.CharField(
        max_length=1, choices=PAYMENT_METHOD_CHOICES, default=PAY_ONLINE
    )
    ref_code = models.CharField(max_length=20, default=create_ref_code, unique=True)
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.PROTECT, related_name='orders')

    def __str__(self):
        return str(self.id) + ' : ' + self.payment_status

    def total_price(self):
        total = 0
        for item in self.items.all():
            total += float(item.unit_price)
        return total * project_variables.TAX + total

    @property
    def jalali_placed_at(self):
        return get_persian_date(self.placed_at)

    class Meta:
        verbose_name = 'سفارش'
        verbose_name_plural = 'آیتم های سفارش'
        indexes = [
            models.Index(fields=['ref_code'])
        ]


class OrderItem(models.Model):
    order = models.ForeignKey(Order, on_delete=models.PROTECT, related_name='items')
    course = models.ForeignKey(Course, on_delete=models.SET_NULL, null=True, related_name='order_items')
    class_gp = models.CharField(max_length=2, default='00')
    course_number = models.PositiveIntegerField()
    contain_telegram = models.BooleanField(default=False)
    contain_sms = models.BooleanField(default=False)
    contain_email = models.BooleanField(default=False)
    unit_price = models.DecimalField(max_digits=10, decimal_places=0)

    def __str__(self):
        return str(self.id) + ' : ' + str(self.order.id) + ' : ' + str(self.course_number) + '_' + self.class_gp

    @staticmethod
    def get_same_items_with_same_course_user(user, course):
        return (OrderItem.objects
                .prefetch_related('order__user')
                .filter(order__user=user,
                        order__payment_status=Order.PAYMENT_STATUS_COMPLETED,
                        course=course)
                .first())

    class Meta:
        verbose_name = 'سفارش'
        verbose_name_plural = 'آیتم های سفارش'
        indexes = [
            models.Index(fields=['course_number', 'class_gp']),
        ]


class WebNotification(models.Model):
    is_read = models.BooleanField(default=False)
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='notifications')
    tracker = models.ForeignKey(ModelTracker, on_delete=models.SET_NULL, related_name='trackers', null=True)
    title = models.CharField(max_length=100)
    text = models.TextField()
    applied_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return str(self.id) + ' : ' + self.title

    @property
    def jalali_applied_at(self):
        return get_persian_date(self.applied_at)

    class Meta:
        verbose_name = 'اعلان'
        verbose_name_plural = 'اعلانات'
        indexes = [
            models.Index(fields=['user', 'is_read'])
        ]


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
