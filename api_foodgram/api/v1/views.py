"""URLs request handlers of the 'api' application."""

from djoser.views import UserViewSet


class CustomUserViewSet(UserViewSet):
    """Modified Djoser UserViewSet."""

    http_method_names = ("get", "post", "head")
