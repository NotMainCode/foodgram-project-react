"""Staff access to the admin site."""

from django.contrib.admin.options import BaseModelAdmin, ModelAdmin


class StaffAllowedBaseModelAdmin(BaseModelAdmin):
    """The staff are allowed access to the Admin site."""

    @staticmethod
    def check_perm(user):
        if user.is_active and (user.is_staff or user.is_superuser):
            return True
        return False

    def has_module_permission(self, request):
        return self.check_perm(request.user)

    def has_view_permission(self, request, obj=None):
        return self.check_perm(request.user)

    def has_add_permission(self, request, obj=None):
        return self.check_perm(request.user)

    def has_change_permission(self, request, obj=None):
        return self.check_perm(request.user)

    def has_delete_permission(self, request, obj=None):
        return self.check_perm(request.user)


class StaffAllowedModelAdmin(ModelAdmin, StaffAllowedBaseModelAdmin):
    """Staff are allowed access to model on the admin site."""
