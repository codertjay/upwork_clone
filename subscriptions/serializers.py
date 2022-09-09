from rest_framework import serializers

from subscriptions.models import Subscription, UserSubscription, Wallet


class SubscriptionSerializer(serializers.ModelSerializer):
    """This subscription is meant to list, create, delete,update  subscription(s)"""

    class Meta:
        model = Subscription
        fields = [
            "id",
            "name",
            "subscription_type",
            "price",
            "timestamp",
        ]
        read_only_fields = ["id", "timestamp"]


class MakePaymentSerializer(serializers.Serializer):
    """this serializer is used for updating the user subscription and the extra fields apart from the
     subscription_id is meant for payment
      which is still under development
     """
    subscription_id = serializers.IntegerField()


class UserSubscriptionSerializer(serializers.ModelSerializer):
    """
    This serializer is meant to view the user subscription
    """
    subscription = SubscriptionSerializer(read_only=True)

    class Meta:
        model = UserSubscription
        fields = [
            "user",
            "subscription",
            "last_payed",
            "timestamp",
        ]


class WalletSerializer(serializers.ModelSerializer):
    """
    This serializer is meant to view wallet balance and all info of a user
    """

    class Meta:
        model = Wallet
        fields = [
            "user",
            "earned",
            "spent",
            "balance",
            "ledger_balance",
            "timestamp",
        ]

