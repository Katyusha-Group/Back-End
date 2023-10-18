from django.dispatch import Signal

wallet_updated_signal = Signal()
# This signal provides following arguments:
# - amount: The amount of money that is added or subtracted from the wallet
# - wallet: The wallet that is updated
