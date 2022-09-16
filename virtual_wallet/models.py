from django.db import models

# Create your models here.
from django.db.models.signals import post_save
from django.utils import timezone

from subscriptions.models import User


class Wallet(models.Model):
    """
    The wallet models enables tracking of the user, by getting info of amount spent, amount earned
    and the user current balance which can be withdrawn
    """
    user = models.OneToOneField(User, related_name="wallet", on_delete=models.CASCADE)
    earned = models.DecimalField(default=0.00, decimal_places=2, max_digits=10000000)
    spent = models.DecimalField(default=0.00, decimal_places=2, max_digits=10000000)
    balance = models.DecimalField(default=0.00, decimal_places=2, max_digits=10000000)
    ledger_balance = models.DecimalField(default=0.00, decimal_places=2, max_digits=10000000)
    timestamp = models.DateTimeField(auto_now_add=timezone.now)


def post_save_create_wallet(sender, instance, *args, **kwargs):
    """
    This creates wallet once a user is being created
    :param instance:  the user created or updated
    """
    if instance:
        wallet, created = Wallet.objects.get_or_create(user=instance)


post_save.connect(post_save_create_wallet, sender=User)

TRANSACTION_TYPE = (
    ('CREDIT', 'CREDIT'),
    ('DEBIT', 'DEBIT')
)


class Transaction(models.Model):
    """
    The transaction that takes place for every funding and crediting for wallet
    """
    user = models.ForeignKey(User, related_name="transactions", on_delete=models.CASCADE)
    transaction_type = models.CharField(choices=TRANSACTION_TYPE, max_length=50)
    previous_balance = models.DecimalField(default=0.00, decimal_places=2, max_digits=10000000)
    current_balance = models.DecimalField(default=0.00, decimal_places=2, max_digits=10000000)
    timestamp = models.DateTimeField(auto_now_add=timezone.now)
