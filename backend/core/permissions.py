from rest_framework import permissions


class IsOwner(permissions.BasePermission):
    """User can only access their own objects."""

    def has_object_permission(self, request, view, obj):
        return getattr(obj, "user", None) == request.user
