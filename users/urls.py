from django.urls import path

from users.views import UserProfileUpdateAPIView, UserUpdateAPIView, FreelancerListAPIView, FreelancerDetailAPIView

urlpatterns = [
    path("profile_update/", UserProfileUpdateAPIView.as_view(), name="profile_update"),
    path("user_update/", UserUpdateAPIView.as_view(), name="user_update"),
    path("freelancers/", FreelancerListAPIView.as_view(), name="freelancers"),
    path("freelancers/<int:pk>/", FreelancerDetailAPIView.as_view(), name="freelancer_detail"),
]
