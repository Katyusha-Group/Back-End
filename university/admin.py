from django import forms

from .models import ExamTimePlace
from django.contrib import admin
from django.db import models

from django_jalali.admin.filters import JDateFieldListFilter

# you need import this for adding jalali calander widget
import django_jalali.admin as jadmin


@admin.register(ExamTimePlace)
class ExamTimePlaceAdmin(admin.ModelAdmin):
    list_filter = (
        ('date', JDateFieldListFilter),
    )

    formfield_overrides = {
        models.DateTimeField: {'widget': jadmin.widgets.AdminjDateWidget}
    }

