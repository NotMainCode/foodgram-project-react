"""Serializers of the 'api' application."""

from djoser.serializers import UserCreateSerializer
from rest_framework import serializers

from users.models import Subscription, User


class CustomUserCreateSerializer(UserCreateSerializer):
    """Modified Djoser UserCreateSerializer."""

    class Meta:
        model = User
        fields = (
            "email",
            "password",
            "id",
            "username",
            "first_name",
            "last_name",
        )


class UserSerializer(serializers.ModelSerializer):
    """Serializer for requests to endpoints of 'Users' resource."""

    is_subscribed = serializers.SerializerMethodField()

    class Meta:
        model = User
        fields = (
            "email",
            "id",
            "username",
            "first_name",
            "last_name",
            "is_subscribed",
        )

    def get_is_subscribed(self, obj):
        try:
            return Subscription.objects.filter(
                subscriber=self.context["request"].user, author=obj
            ).exists()
        except TypeError:
            return False
