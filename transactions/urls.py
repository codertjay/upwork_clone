from django.urls import path

from .views import TransactionListAPIView, TransactionDetailAPIView

urlpatterns = [
    path("", TransactionListAPIView.as_view(), name="transactions"),
    path("<int:id>/", TransactionDetailAPIView.as_view(), name="transaction_detail"),
]
