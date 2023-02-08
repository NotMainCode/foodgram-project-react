"""Custom routers."""

from rest_framework.routers import DefaultRouter


class CustomDefaultRouter(DefaultRouter):
    """Custom DefaultRouter."""

    def get_urls(self):
        """Disable unused endpoints."""
        urls = super().get_urls()
        disable_names = (
            "user-activation",
            "user-resend-activation",
            "user-reset-password",
            "user-reset-password-confirm",
            "user-reset-username",
            "user-reset-username-confirm",
            "user-set-username",
        )
        return list(filter(lambda url: url.name not in disable_names, urls))
