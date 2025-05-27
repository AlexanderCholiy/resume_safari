from typing import Any

from rest_framework import permissions
from rest_framework import request
from rest_framework.views import View


class IsOwnerOrStaffOrAdmin(permissions.BasePermission):
    def has_object_permission(
        self: 'IsOwnerOrStaffOrAdmin', request: request, view: View, obj: Any
    ) -> bool:
        return (
            obj.user == request.user
            or request.user.is_staff
            or request.user.is_superuser
        )


class IsAdminOrStaff(permissions.BasePermission):
    def has_permission(
        self: 'IsAdminOrStaff', request: request, view: View
    ) -> bool:
        return request.user.is_staff or request.user.is_superuser


class IsNotBlocked(permissions.BasePermission):
    def has_permission(
        self: 'IsNotBlocked', request: request, view: View
    ) -> bool:
        return request.user.is_active
