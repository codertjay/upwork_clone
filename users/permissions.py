from decouple import config
from rest_framework.permissions import AllowAny, BasePermission


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
                # return True
                return is_header


class LoggedInPermission(BasePermission):
    """
    Used when the user is logged in we only added this if other verification
    could be needed but right now we are only using the secret header
    """
    message = "Permission Denied"

    def has_permission(self, request, view):
        """By default, headers key are been changed from
                INSTASAW_SK_HEADER to Instasaw-Sk-Header that's why we change the key """
        #  if the user is not authenticated
        if not request.user.is_authenticated:
            return False
        for key, value in request.headers.items():
            print("checking here")
            if key == 'Instasaw-Sk-Header':
                teems_sk_header = request.headers['Instasaw-Sk-Header']
                is_header = teems_sk_header == config('INSTASAW_SK_HEADER')
                # fixme: throttle provide error when  credentials  is passed on TestCase mode
                # return True
                return is_header
