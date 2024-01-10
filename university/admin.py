from django import forms

from .models import ExamTimePlace, CourseTimePlace, Teacher, CourseStudyingGP, BaseCourse, Course, Semester, \
    AllowedDepartment, Department
from django.contrib import admin
from django.db import models


admin.register(CourseTimePlace)
admin.register(ExamTimePlace)
admin.register(Teacher)
admin.register(CourseStudyingGP)
admin.register(BaseCourse)
admin.register(Course)
admin.register(Semester)
admin.register(AllowedDepartment)
admin.register(Department)

