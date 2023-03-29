import uuid

from django.conf import settings
from django.db import models
from django.core.validators import MinValueValidator
from django_jalali.db import models as jmodels


# Create your models here.
class Semester(models.Model):
    year = models.IntegerField(primary_key=True)

    def __str__(self):
        return str(self.year)

    class Meta:
        ordering = ['year']


class Department(models.Model):
    id = models.SmallIntegerField(primary_key=True)
    name = models.CharField(max_length=255, unique=True)


class CourseStudyingGP(models.Model):
    gp_id = models.IntegerField()
    name = models.CharField(max_length=255, unique=True)


class BaseCourse(models.Model):
    course_number = models.IntegerField()
    name = models.CharField(max_length=255)
    total_unit = models.SmallIntegerField(validators=[MinValueValidator(1)])
    practical_unit = models.PositiveSmallIntegerField()
    emergency_deletion = models.BooleanField()
    semester = models.ForeignKey(to=Semester, on_delete=models.PROTECT)
    department = models.ForeignKey(to=Department, on_delete=models.PROTECT)
    course_studying_gp = models.ForeignKey(to=CourseStudyingGP, on_delete=models.PROTECT)


class Course(models.Model):
    class Sex(models.TextChoices):
        MALE = 'C'
        FEMALE = 'F'
        BOTH = 'B'

    class PresentationType(models.TextChoices):
        NORMAL = 'N'
        ELECTRONIC = 'E'
        BOTH = 'B'

    course = models.ForeignKey(to=BaseCourse, on_delete=models.PROTECT)
    class_gp = models.CharField(max_length=2)
    capacity = models.PositiveSmallIntegerField()
    registered_count = models.PositiveSmallIntegerField()
    waiting_count = models.PositiveSmallIntegerField()
    sex = models.CharField(choices=Sex.choices, max_length=1)
    guest_able = models.BooleanField()
    description = models.CharField(max_length=511)
    presentation_type = models.CharField(choices=PresentationType.choices, max_length=1)


class Teacher(models.Model):
    name = models.CharField(max_length=255)
    course = models.ForeignKey(to=Course, on_delete=models.DO_NOTHING)


class ExamTimePlace(models.Model):
    objects = jmodels.jManager()
    date = jmodels.jDateField()
    start_time = models.TimeField()
    end_time = models.TimeField()
    place = models.CharField(max_length=255)
    course = models.ForeignKey(to=Course, on_delete=models.CASCADE)


class CourseTimePlace(models.Model):
    DAYS_CHOICES = [(1, 'شنبه'),
                    (2, 'یکشنبه'),
                    (3, 'دو شنبه'),
                    (4, 'سه شنبه'),
                    (5, 'چهار شنبه'),
                    (6, 'پنجشنبه'),
                    (7, 'جمعه')]

    start_time = models.TimeField()
    end_time = models.TimeField()
    day = models.IntegerField(choices=DAYS_CHOICES)
    place = models.CharField(max_length=255)
    course = models.ForeignKey(to=Course, on_delete=models.CASCADE)
