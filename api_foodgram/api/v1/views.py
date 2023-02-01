"""URLs request handlers of the 'api' application."""

from django.db.models import Exists, OuterRef
from djoser.views import UserViewSet

from users.models import Subscription, User


class CustomUserViewSet(UserViewSet):
    """Modified Djoser UserViewSet."""

    http_method_names = ("get", "post", "head")

    def get_queryset(self):
        qs = User.objects.all()
        if (self.request.method == "GET") and (
            isinstance(self.request.user, User)
        ):
            subquerie = Subscription.objects.filter(
                subscriber=self.request.user, author=OuterRef("pk")
            )
            qs = qs.annotate(is_subscribed=(Exists(subquerie)))
        return qs
