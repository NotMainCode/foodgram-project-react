"""Custom viewsets."""

from abc import ABCMeta

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
    metaclass=ABCMeta,
):
    """Base viewset for resources: Favorites, Subscriptions, Shopping list"""

    model = None
    request_instance_field = None
    request_kwarg = None
    error_message = None

    def create(self, request, *args, **kwargs):
        data = {
            "user": request.user.id,
            self.request_instance_field: kwargs[self.request_kwarg],
        }
        serializer = self.get_serializer_class()(
            data=data, context={"request": request}
        )
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(serializer.data, status=status.HTTP_201_CREATED)

    @action(methods=("delete",), detail=False)
    def delete(self, request, **kwargs):
        try:
            self.model.objects.get(user=request.user, **kwargs).delete()
        except ObjectDoesNotExist:
            raise serializers.ValidationError({"errors": self.error_message})
        return Response(status=status.HTTP_204_NO_CONTENT)
