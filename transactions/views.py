from django.shortcuts import render

# Create your views here.
from rest_framework.generics import ListAPIView, RetrieveAPIView

from transactions.serializers import TransactionSerializer
from users.permissions import LoggedInPermission


class TransactionListAPIView(ListAPIView):
    """
    this class list all transaction of a user
    """
    serializer_class = TransactionSerializer
    permission_classes = [LoggedInPermission]

    def get_queryset(self):
        #  show only the user transaction
        return self.request.user.transactions.all()


class TransactionDetailAPIView(RetrieveAPIView):
    """
    this class list all transaction of a user
    """
    serializer_class = TransactionSerializer
    permission_classes = [LoggedInPermission]
    lookup_field = "id"

    def get_queryset(self):
        #  show only the user transaction
        return self.request.user.transactions.all()
