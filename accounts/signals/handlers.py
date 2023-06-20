from decimal import Decimal

from django.db.models.signals import post_save, pre_delete
from django.dispatch import receiver
from accounts.models import User, Wallet
import custom_config.scripts.signals_requirements as requirements
from accounts.signals import wallet_updated_signal
from custom_config.models import Order
from custom_config.signals import order_created


@receiver(post_save, sender=User)
def create_user_wallet(sender, **kwargs):
    if kwargs['created']:
        user = kwargs['instance']
        wallet = Wallet(
            user=user
        )
        wallet.save()
        user.wallet = wallet
        user.save()


@receiver(wallet_updated_signal)
def create_wallet_transaction(sender, **kwargs):
    amount = kwargs['amount']
    wallet = kwargs['wallet']
    wallet.create_transaction(amount)


@receiver(order_created)
def update_wallet(sender, **kwargs):
    order = kwargs['order']
    if order.payment_method == Order.PAY_WALLET:
        wallet = order.user.wallet
        wallet.balance -= Decimal(order.total_price())
        wallet.save()
        wallet_updated_signal.send(sender=Wallet, wallet=wallet, amount=-order.total_price())
