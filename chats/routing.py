from django.urls import path

from .consumers import ChatConsumer, NotificationConsumer

websocket_urlpatterns = [
    # this url enables creating conversation,messages and viewing all message
    path("chats/<conversation_name>/", ChatConsumer.as_asgi()),
    path("notifications/", NotificationConsumer.as_asgi()),
]