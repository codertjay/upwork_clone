from django.contrib import admin
from django.urls import path, include

from users.views import InstasawLoginAPIView, InstasawRegisterAPIView, RequestEmailOTPAPIView, \
    VerifyEmailOTPAPIView

urlpatterns = [
    path("admin/", admin.site.urls),
    path('api/v1/users/', include("users.urls")),
    path('api/v1/catalogues/', include("catalogues.urls")),
    path('api/v1/categorys/', include("categorys.urls"))

]

"""
The authentication urls which contains login, register, request otp and verify account
"""
auth_urlpatterns = [
    path("api/v1/auth/login/", InstasawLoginAPIView.as_view(), name="instasaw_login"),
    path("api/v1/auth/registration/", InstasawRegisterAPIView.as_view(), name="instasaw_register"),
    #  requesting otp via email
    path("api/v1/auth/request_email_otp/", RequestEmailOTPAPIView.as_view(), name="instasaw_request_otp"),
    #  verify account with the otp passed on posted data
    path("api/v1/auth/verify_account/", VerifyEmailOTPAPIView.as_view(), name="instasaw_verify_account"),
]

urlpatterns += auth_urlpatterns
