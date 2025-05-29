from typing import Any

from rest_framework import permissions
from rest_framework import request
from rest_framework.views import View


class IsOwnerOrStaffOrAdmin(permissions.BasePermission):
    def has_object_permission(
        self: 'IsOwnerOrStaffOrAdmin', request: request, view: View, obj: Any
    ) -> bool:
        return (
            request.user and request.user.is_active and (
                request.user.is_staff
                or request.user.is_superuser
                or obj == request.user
            )
        )


class IsAdminOrStaff(permissions.BasePermission):
    def has_permission(
        self: 'IsAdminOrStaff', request: request, view: View
    ) -> bool:
        return (
            request.user and request.user.is_active and (
                request.user.is_staff
                or request.user.is_superuser
            )
        )
