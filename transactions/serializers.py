from rest_framework import serializers

from transactions.models import Transaction
from users.serializers import UserSerializer


class TransactionSerializer(serializers.ModelSerializer):
    """
    this serializer is used to list and also get the detail of a transaction
    """
    user = UserSerializer(read_only=True)

    class Meta:
        model = Transaction
        fields = [
            "id",
            "user",
            "transaction_id",
            "transaction_type",
            "transaction_stage",
            "transaction_category",
            "amount",
            "previous_balance",
            "current_balance",
            "timestamp",
        ]
