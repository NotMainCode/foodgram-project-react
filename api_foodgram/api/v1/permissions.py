"""Custom permissions."""

from rest_framework.permissions import IsAuthenticatedOrReadOnly, SAFE_METHODS


class IsAuthorOrReadOnly(IsAuthenticatedOrReadOnly):
    """Content author: full access. Other users: reading."""

    message = "You do not have permission to perform this action."

    def has_object_permission(self, request, view, obj):
        return request.method in SAFE_METHODS or request.user == obj.author
