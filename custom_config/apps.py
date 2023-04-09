from django.apps import AppConfig


class CoreConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'custom_config'

    def ready(self):
        from .signals.handlers import create_c_log
        from .signals.handlers import create_u_log
