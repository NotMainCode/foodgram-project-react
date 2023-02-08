"""Custom viewsets."""

from rest_framework import mixins, viewsets


class ListViewSet(
    mixins.ListModelMixin,
    viewsets.GenericViewSet,
):
    """Viewset allows methods: GET(queryset)."""


class ModelViewSetWithoutPUT(viewsets.ModelViewSet):
    """The viewset allows all methods except PUT."""

    http_method_names = ("get", "post", "patch", "delete", "head", "options")