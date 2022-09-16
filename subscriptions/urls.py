from django.urls import path

from .views import UserSubscriptionAPIView

urlpatterns = [

    # this url view th user_subscription and also update the subscription
    path("user_subscription/", UserSubscriptionAPIView.as_view(), name="user_subscription"),

]
