# salons/permissions.py
from rest_framework import permissions


class IsSalonManager(permissions.BasePermission):
    def has_permission(self, request, view):
        return request.user.is_authenticated and request.user.role == 'MANAGER'

    def has_object_permission(self, request, view, obj):
        if hasattr(obj, 'manager'):
            return obj.manager == request.user
        if hasattr(obj, 'salon'):
            return obj.salon.manager == request.user
        return False


class IsSalonStaff(permissions.BasePermission):
    def has_permission(self, request, view):
        return request.user.is_authenticated and request.user.role in ['MANAGER', 'STAFF']

    def has_object_permission(self, request, view, obj):
        if request.user.role == 'MANAGER':
            return True

        if hasattr(obj, 'salon'):
            return True

        return False