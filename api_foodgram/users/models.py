"""Database settings of the 'Users' application."""

from django.contrib.auth.models import AbstractUser
from django.db import models


class User(AbstractUser):
    """Modified model User."""

    first_name = models.CharField(max_length=150)
    last_name = models.CharField(max_length=150)
    email = models.EmailField(unique=True)
    password = models.CharField(max_length=150)

    REQUIRED_FIELDS = ("email", "first_name", "last_name")

    class Meta:
        ordering = ("username",)
        verbose_name = "user"
        verbose_name_plural = "users"

    def __str__(self):
        return self.username


class Subscription(models.Model):
    """Table settings for user subscriptions."""

    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name="subscriber",
    )
    author = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name="subscription",
    )

    class Meta:
        constraints = (
            models.UniqueConstraint(
                fields=["user", "author"], name="unique_subscription"
            ),
        )
