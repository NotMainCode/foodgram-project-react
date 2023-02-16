"""Custom viewsets."""

from django.core.exceptions import ObjectDoesNotExist
from rest_framework import mixins, serializers, status, viewsets
from rest_framework.decorators import action
from rest_framework.response import Response


class GetPostViewSet(
    mixins.CreateModelMixin,
    mixins.RetrieveModelMixin,
    mixins.ListModelMixin,
    viewsets.GenericViewSet,
):
    """The viewset allows methods: GET, POST."""


class GetPostPatchDeleteViewSet(viewsets.ModelViewSet):
    """The viewset allows methods: GET, POST, PATCH, DELETE."""

    http_method_names = ("get", "post", "patch", "delete", "head", "options")


class CustomCreateDestroyViewSet(
    mixins.CreateModelMixin,
    mixins.DestroyModelMixin,
    viewsets.GenericViewSet,
):
    """Base viewset for resources: Favorites, Subscriptions, Shopping list"""

    def get_request_instance_field_kwarg(self):
        return (
            getattr(self, "request_instance_field"),
            getattr(self, "request_kwarg"),
        )

    def get_queryset(self):
        return getattr(self, "model", None).objects.filter(
            user=self.request.user
        )

    def create(self, request, *args, **kwargs):
        instance_field, kwarg = self.get_request_instance_field_kwarg()
        data = {"user": request.user.id, instance_field: kwargs[kwarg]}
        serializer = self.get_serializer_class()(
            data=data, context={"request": request}
        )
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(serializer.data, status=status.HTTP_201_CREATED)

    @action(methods=("delete",), detail=False)
    def delete(self, request, **kwargs):
        try:
            getattr(self, "model", None).objects.get(
                user=request.user, **kwargs
            ).delete()
        except ObjectDoesNotExist:
            raise serializers.ValidationError(
                {"errors": getattr(self, "error_message")}
            )
        return Response(status=status.HTTP_204_NO_CONTENT)
