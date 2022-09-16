from rest_framework import serializers

from virtual_wallet.models import Wallet


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
