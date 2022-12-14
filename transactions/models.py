from django.db import models

# Create your models here.
from django.utils import timezone

from subscriptions.models import User
import uuid

TRANSACTION_TYPE = (
    ('CREDIT', 'CREDIT'),
    ('DEBIT', 'DEBIT')
)
TRANSACTION_STAGE = (
    ('PROCESSING', 'PROCESSING'),
    ('FAILED', 'FAILED'),
    ('SUCCESSFUL', 'SUCCESSFUL'),
)
TRANSACTION_CATEGORY = (
    ('SUBSCRIPTION', 'SUBSCRIPTION'),
    ('AMOUNT FUNDING', 'AMOUNT FUNDING'),
    ('WITHDRAWAL', 'WITHDRAWAL'),
)


class Transaction(models.Model):
    """
    The transaction that takes place for every funding and crediting for wallet
    """
    id = models.UUIDField(
        primary_key=True, default=uuid.uuid4, editable=False, unique=True)
    user = models.ForeignKey(User, related_name="transactions", on_delete=models.CASCADE)
    #  the transaction id is gotten by an external provider
    transaction_id = models.CharField(max_length=250, blank=True, null=True)
    transaction_type = models.CharField(choices=TRANSACTION_TYPE, max_length=50)
    transaction_stage = models.CharField(choices=TRANSACTION_STAGE, max_length=50)
    transaction_category = models.CharField(choices=TRANSACTION_CATEGORY, max_length=50)

    amount = models.DecimalField(max_digits=1000, decimal_places=2)
    previous_balance = models.DecimalField(default=0.00, decimal_places=2, max_digits=1000)
    current_balance = models.DecimalField(default=0.00, decimal_places=2, max_digits=1000)
    timestamp = models.DateTimeField(auto_now_add=timezone.now)

    class Meta:
        ordering = ['-timestamp']

    def refund_balance(self):
        """
        this is used to refund the user wallet if payout failed . then we call this
        :return:
        """
        # Check the stage of the transaction
        # we only refund if the transaction is not successful
        if self.transaction_stage != "SUCCESSFUL":
            user_wallet = self.user.wallet
            #  add the amount
            if user_wallet.fund_balance(self.amount):
                self.transaction_stage == "FAILED"
                # set the user current balance
                self.current_balance = user_wallet.balance
                self.save()
        return True
