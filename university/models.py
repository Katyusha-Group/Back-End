from django.db import models
from django.core.validators import MinValueValidator
from django_jalali.db import models as jmodels

from university import managers
from university.scripts import app_variables


# Create your models here.
class Semester(models.Model):
    year = models.IntegerField(primary_key=True, verbose_name='ترم ارائه درس')

    def __str__(self):
        return str(self.year)

    class Meta:
        ordering = ['-year']
        verbose_name = 'ترم'
        verbose_name_plural = 'ترم ها'


class Department(models.Model):
    department_number = models.SmallIntegerField(primary_key=True,verbose_name= 'کد دانشکده')
    name = models.CharField(max_length=255, unique=True, verbose_name='نام دانشکده')

    def __str__(self):
        return str(self.department_number)

    class Meta:
        verbose_name = 'دانشکده'
        verbose_name_plural = 'دانشکده ها'


class CourseStudyingGP(models.Model):
    gp_id = models.IntegerField(verbose_name='کد گروه آموزشی')
    name = models.CharField(max_length=255, unique=True, verbose_name='نام گروه آموزشی')

    def __str__(self):
        return str(self.gp_id) + ' --- ' + self.name

    class Meta:
        verbose_name = 'گروه آموزشی'
        verbose_name_plural = 'گروه های آموزشی'


class BaseCourse(models.Model):
    course_number = models.IntegerField(primary_key=True, verbose_name='شماره درس', db_index=True)
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

    class Meta:
        verbose_name = 'درس پایه'
        verbose_name_plural = 'دروس پایه'


class Teacher(models.Model):
    name = models.CharField(max_length=255, verbose_name='نام و نام خانوادگی', unique=True, db_index=True)

    class Meta:
        indexes = [
            models.Index(fields=['name', ]),
        ]
        verbose_name = 'استاد'
        verbose_name_plural = 'اساتید'

    def __str__(self):
        return self.name


class Course(models.Model):
    SEX_CHOICES = (
        ('M', app_variables.MAN),
        ('F', app_variables.WOMAN),
        ('B', app_variables.BOTH_SEX),
    )

    PRESENTATION_TYPE_CHOICES = (
        ('N', app_variables.NORMAL),
        ('E', app_variables.ELECTRONIC),
        ('B', app_variables.BOTH_PRESENTATION_TYPE),
        ('A', app_variables.ARCHIVE),
    )

    objects = managers.SignalSenderManager()

    class_gp = models.CharField(max_length=2, verbose_name='گروه درس')
    capacity = models.PositiveSmallIntegerField(verbose_name='ظرفیت')
    registered_count = models.PositiveSmallIntegerField(verbose_name='تعداد ثبت نام شده ها')
    waiting_count = models.PositiveSmallIntegerField(verbose_name='تعداد افراد حاضر در لیست انتظار')
    guest_able = models.BooleanField(verbose_name='قابل اخذ توسط مهمان')
    registration_limit = models.CharField(max_length=1000, verbose_name='محدودیت اخذ')
    description = models.CharField(max_length=400, verbose_name='توضیحات')
    sex = models.CharField(choices=SEX_CHOICES, max_length=1, verbose_name='جنسیت')
    presentation_type = models.CharField(choices=PRESENTATION_TYPE_CHOICES, max_length=1, verbose_name='نحوه ارائه درس')
    base_course = models.ForeignKey(to=BaseCourse, on_delete=models.PROTECT, verbose_name='درس پایه')
    teacher = models.ForeignKey(to=Teacher, on_delete=models.DO_NOTHING, verbose_name='استاد درس')

    def __str__(self):
        return str(self.base_course) + '_' + str(self.class_gp)

    class Meta:
        verbose_name = 'درس'
        verbose_name_plural = 'درس ها'


class ExamTimePlace(models.Model):
    objects = managers.jSignalSenderManager()

    date = jmodels.jDateField(verbose_name='تاریخ امتحان', help_text='سال را به فرم yyyy-mm-dd وارد کنید.')
    start_time = models.TimeField(verbose_name='زمان شروع')
    end_time = models.TimeField(verbose_name='زمان پایان')
    course = models.ForeignKey(to=Course, on_delete=models.CASCADE, verbose_name='درس')

    def __str__(self):
        return str(self.date) + ' ' + str(self.start_time) + ' ' + str(self.end_time)

    class Meta:
        verbose_name = 'تاریخ امتحان'
        verbose_name_plural = 'تاریخ امتحانات'


class CourseTimePlace(models.Model):
    DAYS_CHOICES = [(0, app_variables.SAT),
                    (1, app_variables.SUN),
                    (2, app_variables.MON),
                    (3, app_variables.TUE),
                    (4, app_variables.WED), ]

    objects = managers.SignalSenderManager()

    start_time = models.TimeField(verbose_name='زمان شروع')
    end_time = models.TimeField(verbose_name='زمان پایان')
    day = models.IntegerField(choices=DAYS_CHOICES, verbose_name='روز جلسه')
    place = models.CharField(max_length=255, verbose_name='مکان برگزاری جلسه')
    course = models.ForeignKey(to=Course, on_delete=models.CASCADE, verbose_name='درس')

    def __str__(self):
        return str(self.day) + ' ' + str(self.start_time) + ' ' + str(self.end_time) + ' --- ' + self.place

    class Meta:
        verbose_name = 'زمان و مکان کلاس'
        verbose_name_plural = 'زمان و مکان کلاس ها'
