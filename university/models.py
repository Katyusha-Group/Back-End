from django.db import models
from django.core.validators import MinValueValidator, RegexValidator, MaxValueValidator
from django.conf import settings
from jdatetime import jalali

from university import managers
from utils.model_functions.date import get_persian_date
from utils.variables import project_variables
from utils.variables.project_variables import day_mapper


# Create your models here.
class Semester(models.Model):
    objects = managers.SignalSenderManager()

    year = models.IntegerField(primary_key=True, verbose_name='ترم ارائه درس')

    def __str__(self):
        return str(self.year)

    class Meta:
        ordering = ['-year']
        verbose_name = 'ترم'
        verbose_name_plural = 'ترم ها'


class Department(models.Model):
    objects = managers.SignalSenderManager()

    department_number = models.PositiveSmallIntegerField(primary_key=True, verbose_name='کد دانشکده')
    name = models.CharField(max_length=50, unique=True, verbose_name='نام دانشکده')

    def __str__(self):
        return str(self.name)

    class Meta:
        verbose_name = 'دانشکده'
        verbose_name_plural = 'دانشکده ها'


class CourseStudyingGP(models.Model):
    objects = managers.SignalSenderManager()

    gp_id = models.PositiveSmallIntegerField(verbose_name='کد گروه آموزشی')
    name = models.CharField(max_length=50, unique=True, verbose_name='نام گروه آموزشی')

    def __str__(self):
        return str(self.gp_id) + ' --- ' + self.name

    class Meta:
        verbose_name = 'گروه آموزشی'
        verbose_name_plural = 'گروه های آموزشی'


class BaseCourse(models.Model):
    objects = managers.SignalSenderManager()

    course_number = models.IntegerField(primary_key=True, verbose_name='شماره درس', db_index=True,
                                        validators=[MinValueValidator(1000000), MaxValueValidator(9999999)])
    name = models.CharField(max_length=50, verbose_name='نام درس')
    total_unit = models.FloatField(validators=[MinValueValidator(0)], verbose_name='کل واحد')
    practical_unit = models.FloatField(validators=[MinValueValidator(0)], verbose_name='واحد های عملی')
    emergency_deletion = models.BooleanField(verbose_name='حذف اضطراری')
    department = models.ForeignKey(to=Department, on_delete=models.CASCADE, verbose_name='دانشکده درس',
                                   related_name='base_courses')
    course_studying_gp = models.ForeignKey(to=CourseStudyingGP, on_delete=models.CASCADE,
                                           verbose_name='دوره آموزشی درس')

    def get_default_profile_name(self):
        return str(self.name)

    def get_default_profile_username(self):
        return 'C_' + str(self.course_number)

    def get_default_profile_image(self):
        return 'images/profile_pics/course_default.png'

    def __str__(self):
        return str(self.course_number) + ' --- ' + self.name

    class Meta:
        verbose_name = 'درس پایه'
        verbose_name_plural = 'دروس پایه'


class Teacher(models.Model):
    objects = managers.SignalSenderManager()

    name = models.CharField(max_length=50, verbose_name='نام و نام خانوادگی', unique=True, db_index=True)
    golestan_name = models.CharField(max_length=50, verbose_name='نام و نام خانوادگی', unique=True, db_index=True)
    email_address = models.CharField(max_length=255, verbose_name='ایمیل', null=True, blank=True)
    lms_id = models.PositiveIntegerField(verbose_name='شماره استاد در سامانه LMS', null=True, blank=True)
    teacher_image_url = models.CharField(max_length=255, verbose_name='آدرس تصویر استاد', null=True, blank=True)
    teacher_image = models.ImageField(upload_to='images/teachers_image/', verbose_name='تصویر استاد',
                                      default='images/teachers_image/default.png', blank=True)
    teacher_lms_image = models.ImageField(upload_to='images/teachers_image/', verbose_name='تصویر استاد',
                                          default='images/teachers_image/default.png', blank=True)

    class Meta:
        indexes = [
            models.Index(fields=['name', ]),
        ]
        verbose_name = 'استاد'
        verbose_name_plural = 'اساتید'

    def get_default_profile_name(self):
        return self.name

    def get_default_profile_username(self):
        return 'T_' + str(self.id)

    def get_default_profile_image(self):
        return self.teacher_image

    def __str__(self):
        return self.name


class Course(models.Model):
    SEX_CHOICES = (
        ('M', project_variables.MAN_FA),
        ('F', project_variables.WOMAN_FA),
        ('B', project_variables.BOTH_SEX_FA),
    )

    PRESENTATION_TYPE_CHOICES = (
        ('N', project_variables.NORMAL),
        ('E', project_variables.ELECTRONIC),
        ('B', project_variables.BOTH_PRESENTATION_TYPE),
        ('A', project_variables.ARCHIVE),
    )

    objects = managers.SignalSenderManager()

    class_gp = models.CharField(max_length=2, verbose_name='گروه درس')
    capacity = models.SmallIntegerField(verbose_name='ظرفیت', validators=[MinValueValidator(0)])
    registered_count = models.SmallIntegerField(verbose_name='تعداد ثبت نام شده ها', validators=[MinValueValidator(0)])
    waiting_count = models.SmallIntegerField(verbose_name='تعداد افراد حاضر در لیست انتظار',
                                             validators=[MinValueValidator(0)])
    guest_able = models.BooleanField(verbose_name='قابل اخذ توسط مهمان')
    registration_limit = models.CharField(max_length=2000, verbose_name='محدودیت اخذ')
    description = models.CharField(max_length=400, verbose_name='توضیحات')
    sex = models.CharField(choices=SEX_CHOICES, max_length=1, verbose_name='جنسیت')
    presentation_type = models.CharField(choices=PRESENTATION_TYPE_CHOICES, max_length=1, verbose_name='نحوه ارائه درس')
    base_course = models.ForeignKey(to=BaseCourse, on_delete=models.CASCADE, verbose_name='درس پایه',
                                    related_name='courses')
    teachers = models.ManyToManyField(to=Teacher, verbose_name='اساتید', related_name='courses')
    students = models.ManyToManyField(to=settings.AUTH_USER_MODEL, related_name='courses')
    semester = models.ForeignKey(to=Semester, on_delete=models.CASCADE, verbose_name='ترم ارائه',
                                 related_name='courses')

    def __str__(self):
        return str(self.base_course.course_number) + '_' + str(self.class_gp)

    class Meta:
        verbose_name = 'درس'
        verbose_name_plural = 'درس ها'
        unique_together = ('class_gp', 'base_course', 'semester')


class ExamTimePlace(models.Model):
    objects = managers.SignalSenderManager()

    date = models.DateField(verbose_name='تاریخ امتحان', help_text='سال را به فرم yyyy-mm-dd وارد کنید.')
    start_time = models.TimeField(verbose_name='زمان شروع')
    end_time = models.TimeField(verbose_name='زمان پایان')
    course = models.ForeignKey(to=Course, on_delete=models.CASCADE, verbose_name='درس', related_name='exam_times')

    def __str__(self):
        return self.get_persian_date()

    def get_persian_date(self):
        return get_persian_date(self.date)

    class Meta:
        verbose_name = 'تاریخ امتحان'
        verbose_name_plural = 'تاریخ امتحانات'


class CourseTimePlace(models.Model):
    DAYS_CHOICES = [(project_variables.SAT_NUMBER, project_variables.SAT),
                    (project_variables.SUN_NUMBER, project_variables.SUN),
                    (project_variables.MON_NUMBER, project_variables.MON),
                    (project_variables.TUE_NUMBER, project_variables.TUE),
                    (project_variables.WED_NUMBER, project_variables.WED), ]

    objects = managers.SignalSenderManager()

    start_time = models.TimeField(verbose_name='زمان شروع')
    end_time = models.TimeField(verbose_name='زمان پایان')
    day = models.IntegerField(choices=DAYS_CHOICES, verbose_name='روز جلسه')
    place = models.CharField(max_length=255, verbose_name='مکان برگزاری جلسه')
    course = models.ForeignKey(to=Course, on_delete=models.CASCADE, verbose_name='درس', related_name='course_times')

    def __str__(self):
        return day_mapper[self.day] + ' - ' + str(self.start_time) + ' - ' + str(
            self.end_time) + ' --- ' + self.place

    class Meta:
        verbose_name = 'زمان و مکان کلاس'
        verbose_name_plural = 'زمان و مکان کلاس ها'


class AllowedDepartment(models.Model):
    objects = managers.SignalSenderManager()

    department = models.ForeignKey(to=Department, on_delete=models.CASCADE, verbose_name='دانشکده',
                                   related_name='allowed_departments')
    course = models.ForeignKey(to=Course, on_delete=models.CASCADE, verbose_name='درس',
                               related_name='allowed_departments')

    def __str__(self):
        return str(self.department.name)

    class Meta:
        verbose_name = 'دانشکدۀ مجاز و غیر مجاز'
        verbose_name_plural = 'دانشکده های مجاز و غیر مجاز'
