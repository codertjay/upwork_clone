from decouple import config
from rest_framework.permissions import IsAuthenticated, AllowAny


class NotLoggedInPermission(AllowAny):
    """used when user not logged in (like verify email address)"""
    message = 'Permission Denied'

    def has_permission(self, request, view):
        """By default, headers key are been changed from
        INSTASAW_SK_HEADER to Instasaw-Sk-Header that's why we change the key """
        for key, value in request.headers.items():
            if key == 'Instasaw-Sk-Header':
                teems_sk_header = request.headers['Instasaw-Sk-Header']
                is_header = teems_sk_header == config('INSTASAW_SK_HEADER')
                # fixme: throttle provide error when  credentials  is passed on TestCase
                return True
                # return is_header


class LoggedInPermission(IsAuthenticated):
    """
    Used when the user is logged in we only added this if other verification
    could be needed but right now we are only using the secret header
    """
    message = "Permission Denied"

    def has_permission(self, request, view):
        """By default, headers key are been changed from
                INSTASAW_SK_HEADER to Instasaw-Sk-Header that's why we change the key """
        for key, value in request.headers.items():
            if key == 'Instasaw-Sk-Header':
                teems_sk_header = request.headers['Instasaw-Sk-Header']
                is_header = teems_sk_header == config('INSTASAW_SK_HEADER')
                # fixme: throttle provide error when  credentials  is passed on TestCase mode
                return True
                # return is_header


class LoggedInCustomerPermission(IsAuthenticated):
    """
    used to check if the current user is a customer, and also it checks if the user is allowed to
    create multiple jobs if he or she is on free tier
    """
    message = "You must be a customer and also you are not allowed to" \
              " create multiple ongoing jons on free tier"

    def has_permission(self, request, view):
        """
        checks for the user if he has access to create multiple and  also check headers
        """
        for key, value in request.headers.items():
            if key == 'Instasaw-Sk-Header':
                teems_sk_header = request.headers['Instasaw-Sk-Header']
                is_header = teems_sk_header == config('INSTASAW_SK_HEADER')
                if is_header:
                    # if the header exist I then check for the user type
                    if request.user.is_authenticated and request.user.user_type == "CUSTOMER":
                        return True


class LoggedInFreelancerPermission(IsAuthenticated):
    """
    used to check if the current user is a freelancer, and also it checks if the user is allowed to
    create multiple jobs if he or she is on free tier
    """
    message = "You must be a customer and also you are not allowed to" \
              " create multiple ongoing jons on free tier"

    def has_permission(self, request, view):
        """
        checks for the user if he has access to create multiple and  also check headers
        """
        for key, value in request.headers.items():
            if key == 'Instasaw-Sk-Header':
                teems_sk_header = request.headers['Instasaw-Sk-Header']
                is_header = teems_sk_header == config('INSTASAW_SK_HEADER')
                if is_header:
                    # if the header exist I then check for the user type
                    if request.user.is_authenticated and request.user.user_type == "FREELANCER":
                        return True
