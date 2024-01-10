from rest_framework.exceptions import ValidationError


def not_null(value, message):
    if value is None:
        raise ValidationError(message)
    return value
