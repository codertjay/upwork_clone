from django.urls import path

from .views import ChatListCreateAPIView, ChatRetrieveUpdateDestroyAPIView

urlpatterns = [
    # Job routes
    path("", ChatListCreateAPIView.as_view(), name="list_chats"),
    path("<int:pk>/", ChatRetrieveUpdateDestroyAPIView.as_view(), name="chat_retrieve_update_destroy"),
]
