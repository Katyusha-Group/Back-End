import django_filters
from django_filters.rest_framework import FilterSet
from .models import Course


class CourseFilter(FilterSet):
    department_pk = django_filters.NumberFilter(field_name='base_course__department__department_number')

    class Meta:
        model = Course
        fields = ['department_pk']