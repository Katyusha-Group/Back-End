import uuid

from django.conf import settings
from django.db import models
from django.core.validators import MinValueValidator
from django_jalali.db import models as jmodels


# Create your models here.
class Semester(models.Model):
    year = models.IntegerField(primary_key=True, verbose_name='ترم ارائه درس')

    def __str__(self):
        return str(self.year)

    class Meta:
        ordering = ['year']


class Department(models.Model):
    department_number = models.SmallIntegerField(primary_key=True, verbose_name='کد دانشکده')
    name = models.CharField(max_length=255, unique=True, verbose_name='نام دانشکده')

    def __str__(self):
        return str(self.department_number)


class CourseStudyingGP(models.Model):
    gp_id = models.IntegerField(verbose_name='کد دوره آموزشی')
    name = models.CharField(max_length=255, unique=True, verbose_name='نام دوره آموزشی')

    def __str__(self):
        return str(self.gp_id) + ' --- ' + self.name


class BaseCourse(models.Model):
    course_number = models.IntegerField(primary_key=True, verbose_name='شماره درس')
    name = models.CharField(max_length=255, verbose_name='نام درس')
    total_unit = models.SmallIntegerField(validators=[MinValueValidator(1)], verbose_name='کل واحد')
    practical_unit = models.PositiveSmallIntegerField(verbose_name='واحد های عملی')
    emergency_deletion = models.BooleanField(verbose_name='حذف اضطراری')
    semester = models.ForeignKey(to=Semester, on_delete=models.PROTECT, verbose_name='ترم ارائه')
    department = models.ForeignKey(to=Department, on_delete=models.PROTECT, verbose_name='دانشکده درس')
    course_studying_gp = models.ForeignKey(to=CourseStudyingGP, on_delete=models.PROTECT,
                                           verbose_name='دوره آموزشی درس')

    def __str__(self):
        return str(self.course_number) + ' --- ' + self.name


class Teacher(models.Model):
    name = models.CharField(max_length=255, verbose_name='نام و نام خانوادگی')

    def __str__(self):
        return self.name + ' : ' + self.course_set


class Course(models.Model):
    class Sex(models.TextChoices):
        MALE = 'C'
        FEMALE = 'F'
        BOTH = 'B'

    class PresentationType(models.TextChoices):
        NORMAL = 'N'
        ELECTRONIC = 'E'
        BOTH = 'B'

    class_gp = models.CharField(max_length=2, verbose_name='گروه درس')
    capacity = models.PositiveSmallIntegerField(verbose_name='ظرفیت')
    registered_count = models.PositiveSmallIntegerField(verbose_name='تعداد ثبت نام شده ها')
    waiting_count = models.PositiveSmallIntegerField(verbose_name='تعداد افراد حاضر در لیست انتظار')
    sex = models.CharField(choices=Sex.choices, max_length=1, verbose_name='جنسیت')
    guest_able = models.BooleanField(verbose_name='قابل اخذ توسط مهمان')
    description = models.CharField(max_length=511, verbose_name='توضیحات')
    presentation_type = models.CharField(choices=PresentationType.choices, max_length=1, verbose_name='نحوه ارائه درس')
    base_course = models.ForeignKey(to=BaseCourse, on_delete=models.PROTECT, verbose_name='درس پایه')
    teacher = models.ForeignKey(to=Teacher, on_delete=models.DO_NOTHING, verbose_name='استاد درس')

    def __str__(self):
        return str(self.base_course.course_number) + '-' + self.class_gp + ' --- ' + self.base_course.name


class ExamTimePlace(models.Model):
    objects = jmodels.jManager()
    date = jmodels.jDateField(verbose_name='تاریخ امتحان', help_text='سال را به فرم yyyy-mm-dd وارد کنید.')
    start_time = models.TimeField(verbose_name='زمان شروع')
    end_time = models.TimeField(verbose_name='زمان پایان')
    place = models.CharField(max_length=255, verbose_name='مکان امتحان')
    course = models.ForeignKey(to=Course, on_delete=models.CASCADE, verbose_name='درس')

    def __str__(self):
        return str(self.date) + ' ' + str(self.start_time) + ' ' + str(self.end_time) + ' --- ' + self.place


class CourseTimePlace(models.Model):
    DAYS_CHOICES = [(1, 'شنبه'),
                    (2, 'یکشنبه'),
                    (3, 'دو شنبه'),
                    (4, 'سه شنبه'),
                    (5, 'چهار شنبه'),
                    (6, 'پنجشنبه'),
                    (7, 'جمعه')]

    start_time = models.TimeField(verbose_name='زمان شروع')
    end_time = models.TimeField(verbose_name='زمان پایان')
    day = models.IntegerField(choices=DAYS_CHOICES, verbose_name='روز جلسه')
    place = models.CharField(max_length=255, verbose_name='مکان برگزاری جلسه')
    course = models.ForeignKey(to=Course, on_delete=models.CASCADE, verbose_name='درس')

    def __str__(self):
        return str(self.day) + ' ' + str(self.start_time) + ' ' + str(self.end_time) + ' --- ' + self.place
