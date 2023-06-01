from django.apps import AppConfig
from django.db.models import signals


class UniversityConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'university'

