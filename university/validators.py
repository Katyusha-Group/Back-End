from django.core import validators
from django.db.models import QuerySet
from rest_framework.exceptions import ValidationError


def validate_int(expected_int, message):
    try:
        validators.validate_integer(expected_int)
    except ValidationError:
        raise ValidationError({'detail': message})


def validate_queryset_existence(queryset: QuerySet, message: str):
    if not queryset.exists():
        raise ValidationError({'detail': 'course does not exist'})
