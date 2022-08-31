from django.urls import path

from users.views import UserProfileUpdateAPIView

urlpatterns = [
    path("profile_update/", UserProfileUpdateAPIView.as_view(), name="profile_update"),
]
