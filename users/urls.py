from django.urls import path

from users.views import UserProfileUpdateAPIView, UserUpdateAPIView

urlpatterns = [
    path("profile_update/", UserProfileUpdateAPIView.as_view(), name="profile_update"),
    path("user_update/", UserUpdateAPIView.as_view(), name="user_update"),
]
