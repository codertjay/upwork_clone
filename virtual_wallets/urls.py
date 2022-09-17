from django.urls import path

from .views import WalletAPIView, CreatePaymentAPIView, ApprovePaymentAPIView, WithdrawFundAPIView

urlpatterns = [
    path("wallet/", WalletAPIView.as_view(), name="wallet"),
    path("create_payment/", CreatePaymentAPIView.as_view(), name="create_payment"),
    path("approve_payment/", ApprovePaymentAPIView.as_view(), name="approve_payment"),
    path("withdraw/", WithdrawFundAPIView.as_view(), name="withdraw"),
]
