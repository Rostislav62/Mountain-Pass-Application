from rest_framework.permissions import BasePermission


class IsSuperAdmin(BasePermission):
    """Разрешение для главного администратора. IsSuperAdmin – Полный доступ (PUT, DELETE, POST)."""

    def has_permission(self, request, view):
        return request.user.is_authenticated and request.user.is_super_admin


class IsModerator(BasePermission):
    """Разрешение для модераторов. IsModerator – Может работать с модерацией (approve, reject)."""

    def has_permission(self, request, view):
        return request.user.is_authenticated and hasattr(request.user, "moderator_group")


class ReadOnlyAdmin(BasePermission):
    """Разрешение для обычных администраторов (только чтение). ReadOnlyAdmin – Только GET (просмотр)."""

    def has_permission(self, request, view):
        return request.user.is_authenticated and request.user.is_staff and not request.user.is_super_admin

    def has_object_permission(self, request, view, obj):
        return request.method in ["GET", "HEAD", "OPTIONS"]


class IsAuthenticatedAndSuperAdmin(BasePermission):
    """Разрешение: только для администраторов"""
    def has_permission(self, request, view):
        return request.user.is_authenticated and request.user.is_superuser



