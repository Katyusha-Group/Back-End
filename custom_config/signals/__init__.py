from django.dispatch import Signal

order_created = Signal()
# This signal provides following arguments:
# - order: The order that is created
# - total_price: The total price of the order
