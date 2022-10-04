from django.db import models
import uuid

# Create your models here.
from django.db.models.signals import post_save
from django.utils import timezone
from django.conf import settings
from subscriptions.models import User

#  payout percent fee
PAYOUT_PERCENT_FEE = settings.PAYPAL_PAYOUT_PERCENT_FEE


class Wallet(models.Model):
    """
    The wallet models enables tracking of the user, by getting info of amount spent, amount earned
    and the user current balance which can be withdrawn
    """
    id = models.UUIDField(
        primary_key=True, default=uuid.uuid4(), editable=False, unique=True)
    user = models.OneToOneField(User, related_name="wallet", on_delete=models.CASCADE)

    balance = models.DecimalField(default=0.00, decimal_places=2, max_digits=1000)
    #  having issues managing the ledger balance since i don't have a wallet id to check
    # ledger_balance = models.DecimalField(default=0.00, decimal_places=2, max_digits=1000)
    timestamp = models.DateTimeField(auto_now_add=timezone.now)

    class Meta:
        ordering = ['-timestamp']

    def can_withdraw(self, amount):
        """this functions check if the amount passed is greater than the balance to prevent users from withdrawing more
        than
        """
        if self.balance > amount:
            return True
        return False

    def fund_balance(self, amount: float):
        """this is used to fund the user wallet once the amount is provided"""
        self.balance += amount
        self.save()
        return True

    def withdraw_balance(self, amount: float):
        """this is used to withdraw the user wallet once the amount is provided"""
        if self.can_withdraw(amount):
            self.balance -= amount
            self.save()
            return True
        return False


def post_save_create_wallet(sender, instance, *args, **kwargs):
    """
    This creates wallet once a user is being created
    :param instance:  the user created or updated
    """
    if instance:
        wallet, created = Wallet.objects.get_or_create(user=instance)


post_save.connect(post_save_create_wallet, sender=User)
