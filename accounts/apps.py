from django.apps import AppConfig


class AccountsConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'accounts'

    def ready(self):
        from .signals.handlers import create_user_wallet
        from .signals.handlers import create_wallet_transaction
        from .signals.handlers import update_wallet
        from .signals.handlers import create_profile
