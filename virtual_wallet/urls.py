from django.urls import path

from .views import  WalletAPIView

urlpatterns = [
    path("wallet/", WalletAPIView.as_view(), name="wallet"),

]
