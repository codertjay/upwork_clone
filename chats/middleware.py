from urllib.parse import parse_qs
from channels.db import database_sync_to_async

from django.contrib.auth import get_user_model
from django.http import Http404
from django.utils.translation import gettext_lazy as _
from rest_framework.exceptions import AuthenticationFailed
from rest_framework_simplejwt.tokens import AccessToken

User = get_user_model()


class TokenAuthentication:
    """
    Simple token based authentication.

    Clients should authenticate by passing the token key in the query parameters.
    For example:

        ?token=401f7ac837da42b97f613d789819ff93537bee6a
    """

    model = None

    def get_model(self):
        if self.model is not None:
            return self.model
        from rest_framework_simplejwt.tokens import AccessToken
        return AccessToken

    """
    A custom token model may be used, but must have the following properties.

    * key -- The string identifying the token
    * user -- The user to which the token belongs
    """

    def authenticate_credentials(self, key):
        """
        This is used to verify the user credentials using the token provided on the url
        :param key:  the token key
        :return:
        """
        token = AccessToken(token=key)
        try:
            user_id = token.get("user_id")
            if not user_id:
                raise AuthenticationFailed("Invalid token")
            user = User.objects.get(id=user_id)
        except Exception as a:
            raise AuthenticationFailed(_("Invalid token."))
        if not user.is_active:
            raise AuthenticationFailed(_("User inactive or deleted."))
        return user


@database_sync_to_async
def get_user(scope):
    """
    Return the user model instance associated with the given scope.
    If no user is retrieved, return an instance of `AnonymousUser`.
    """
    # postpone model import to avoid ImproperlyConfigured error before Django
    # setup is complete.
    from django.contrib.auth.models import AnonymousUser

    if "token" not in scope:
        raise ValueError(
            "Cannot find token in scope. You should wrap your consumer in "
            "TokenAuthMiddleware."
        )
    token = scope["token"][0]
    if not token:
        raise AuthenticationFailed("No token passed on params")
    user = None
    try:
        auth = TokenAuthentication()
        user = auth.authenticate_credentials(token)
    except AuthenticationFailed:
        pass
    return user or AnonymousUser()


class TokenAuthMiddleware:
    """
    Custom middleware that takes a token from the query string and authenticates via
    Django Rest Framework authtoken.
    """

    def __init__(self, app):
        # Store the ASGI application we were passed
        self.app = app

    async def __call__(self, scope, receive, send):
        # Look up user from query string (you should also do things like
        # checking if it is a valid user ID, or if scope["user"] is already
        # populated).
        query_params = parse_qs(scope["query_string"].decode())
        token = query_params.get("token")
        scope["token"] = token
        scope["user"] = await get_user(scope)
        return await self.app(scope, receive, send)
