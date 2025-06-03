from typing import Any

from rest_framework import permissions
from rest_framework.request import Request
from rest_framework.views import View


class StaffOrReadOnly(permissions.BasePermission):

    def has_permission(
        self: 'StaffOrReadOnly', request: Request, view: View
    ) -> bool:
        if request.method in permissions.SAFE_METHODS:
            return True
        return request.user.is_authenticated and (
            request.user.is_staff or request.user.is_superuser
        )

    def has_object_permission(
        self: 'StaffOrReadOnly', request: Request, view: View, obj: Any
    ) -> bool:
        if request.method in permissions.SAFE_METHODS:
            return True
        return request.user.is_authenticated and (
            request.user.is_staff or request.user.is_superuser
        )
