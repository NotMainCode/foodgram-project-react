"""Admin site settings of the 'Users' application."""

from django.contrib import admin
from django.contrib.auth.admin import UserAdmin

from users.models import User


@admin.register(User)
class CustomUserAdmin(UserAdmin):
    """Table settings for resource 'Users' on the admin site."""

    def get_queryset(self, request):
        """Custom queryset of User model instances."""

        qs = User.objects.all()
        if not request.user.is_superuser:
            qs = qs.filter(is_superuser=False, is_staff=False)
        ordering = self.get_ordering(request)
        if ordering:
            qs = qs.order_by(*ordering)
        return qs

    def has_module_permission(self, request):
        return True

    def has_add_permission(self, request):
        return True

    def has_change_permission(self, request, obj=None):
        return True

    def has_delete_permission(self, request, obj=None):
        if obj is not None and obj == request.user:
            return False
        return True

    def get_form(self, request, obj=None, **kwargs):
        """Restrict access to fields of forms  for non-superusers."""
        form = super().get_form(request, obj, **kwargs)
        if request.user.is_superuser:
            return form
        disabled_fields = (
            "date_joined",
            "last_login",
            "groups",
            "user_permissions",
            "is_staff",
            "is_superuser",
        )
        for field in disabled_fields:
            if field in form.base_fields:
                form.base_fields[field].disabled = True
        return form

    def activate_users(self, request, queryset):
        """Admin actions: activate users."""
        count = queryset.filter(is_active=False).update(is_active=True)
        self.message_user(request, "Activated {} users.".format(count))

    def deactivate_users(self, request, queryset):
        """Admin actions: deactivate users."""
        count = queryset.filter(is_active=True).update(is_active=False)
        self.message_user(request, "Deactivated {} users.".format(count))

    list_display = (
        "pk",
        "username",
        "email",
        "first_name",
        "last_name",
        "is_staff",
        "is_active",
    )
    search_fields = ("username",)
    list_filter = ("username", "email")
    readonly_fields = (
        "date_joined",
        "last_login",
    )
    actions = (
        "activate_users",
        "deactivate_users",
    )
    activate_users.short_description = "Activate Users"
    deactivate_users.short_description = "Deactivate Users"
