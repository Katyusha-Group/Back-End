from django.db.models.signals import post_save, pre_delete
from django.dispatch import receiver
from accounts.models import User, Wallet
import custom_config.scripts.signals_requirements as requirements
from accounts.signals import wallet_updated_signal


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


@receiver(wallet_updated_signal, sender=Wallet)
def create_wallet_transaction(sender, **kwargs):
    amount = kwargs['amount']
    wallet = kwargs['instance']
    wallet.create_transaction(amount)
