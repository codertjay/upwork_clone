from django.urls import path

from .views import CreateWebhookAPIView, ListenToWebhookAPIView, DeleteWebhookAPIView

urlpatterns = [
    # this url view th user_subscription and also update the subscription
    path("create_webhook/", CreateWebhookAPIView.as_view(), name="create_webhook"),
    path("delete_webhook/", DeleteWebhookAPIView.as_view(), name="delete_webhook"),
    path("listen_to_webhook/", ListenToWebhookAPIView.as_view(), name="Listen_to_webhook"),

]
