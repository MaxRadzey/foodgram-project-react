from rest_framework import permissions


class IsOwnerOrReadOnly(permissions.BasePermission):
    """Класс ограничения прав пользователя."""

    def has_object_permission(self, request, view, obj):
        """Возвращает True если пользователь - автор."""
        return (
            obj.author == request.user
            or request.method in permissions.SAFE_METHODS
        )


class IsAdminOrReadOnly(permissions.BasePermission):
    """Класс ограничения прав пользователя."""

    def has_permission(self, request, view):
        """Возвращает True если пользователь - админ."""
        return (
            request.method in permissions.SAFE_METHODS
            or request.user.is_staff)
