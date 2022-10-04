from rest_framework import serializers

from users.serializers import UserSerializer
from virtual_wallets.models import Wallet


class WalletSerializer(serializers.ModelSerializer):
    """
    This serializer is meant to view wallet balance and all info of a user
    """
    user = UserSerializer(read_only=True)

    class Meta:
        model = Wallet
        fields = [
            "user",
            "balance",
            "timestamp",
        ]


class CreatePaymentSerializer(serializers.Serializer):
    """
    this serializer is used to fund the wallet using PayPal
    used by the Create payment class
    """
    amount = serializers.DecimalField(max_digits=1000, decimal_places=2)


class ApprovePaymentSerializer(serializers.Serializer):
    """
    this serializer is used to approve payment .
    after a successful payment we need to approve it also  using the id gotten from PayPal create payment
    """
    transaction_id = serializers.CharField(max_length=250)


class WithdrawFundSerializer(serializers.Serializer):
    """this class is meant to withdraw fund of a user using the amount provided,
     the email address of his existing paypal account, or he would need to create
     a paypal account with that email to withdraw the fund
     """
    amount = serializers.DecimalField(max_digits=1000, decimal_places=2)
    otp = serializers.IntegerField(min_value=1000)
