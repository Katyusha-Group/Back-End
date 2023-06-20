from django.dispatch import Signal

wallet_updated_signal = Signal(providing_args=['amount', 'wallet'])
