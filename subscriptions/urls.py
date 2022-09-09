from django.urls import path

from .views import CreateSubscriptionAPIView, ListSubscriptionsAPIView, RetrieveUpdateDestroySubscriptionAPIView, \
    UserSubscriptionAPIView, WalletAPIView

urlpatterns = [
    path("", ListSubscriptionsAPIView.as_view(), name="list_subscriptions"),
    path("<int:pk>/", RetrieveUpdateDestroySubscriptionAPIView.as_view(), name="create_retrieve_destroy"),
    path("create/", CreateSubscriptionAPIView.as_view(), name="create_subscription"),
    path("user_subscription/", UserSubscriptionAPIView.as_view(), name="create_retrieve_destroy"),
    path("wallet/", WalletAPIView.as_view(), name="wallet"),

]
