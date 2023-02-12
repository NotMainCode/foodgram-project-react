"""Custom viewsets."""

from rest_framework import mixins, viewsets


class ListViewSet(
    mixins.ListModelMixin,
    viewsets.GenericViewSet,
):
    """Viewset allows methods: GET(queryset)."""


class GetPostPatchDeleteViewSet(viewsets.ModelViewSet):
    """The viewset allows methods: GET, POST, PATCH, DELETE."""

    http_method_names = ("get", "post", "patch", "delete", "head", "options")


class CreateDestroyViewSet(
    mixins.CreateModelMixin,
    mixins.DestroyModelMixin,
    viewsets.GenericViewSet,
):
    """Viewset allows methods: POST, DELETE."""
