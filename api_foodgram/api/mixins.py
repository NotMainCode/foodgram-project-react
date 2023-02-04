"""Custom viewsets."""

from rest_framework import mixins, viewsets


class CreateDestroyViewSet(
    mixins.CreateModelMixin,
    mixins.DestroyModelMixin,
    viewsets.GenericViewSet,
):
    """Viewset allows methods: POST, DELETE."""
