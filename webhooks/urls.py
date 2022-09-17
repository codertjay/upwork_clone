from django.urls import path

from .views import CreateWebhookAPIView, ListenToWebhookEventAPIView, DeleteWebhookAPIView, WebhookEventListAPIView, \
    WebhookEventDetailAPIView

urlpatterns = [
    # this url view th user_subscription and also update the subscription
    path("create_webhook/", CreateWebhookAPIView.as_view(), name="create_webhook"),
    path("delete_webhook/", DeleteWebhookAPIView.as_view(), name="delete_webhook"),
    path("listen_to_webhook/", ListenToWebhookEventAPIView.as_view(), name="Listen_to_webhook"),
    path("webhook_events/", WebhookEventListAPIView.as_view(), name="webhook_events"),
    path("webhook_events/<int:id>/", WebhookEventDetailAPIView.as_view(), name="webhook_event_detail"),

]
