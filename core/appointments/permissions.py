# appointments/permissions.py
from rest_framework import permissions

class IsSalonManager(permissions.BasePermission):
    def has_permission(self, request, view):
        return request.user.is_authenticated and request.user.role == 'MANAGER'

class IsStaffMember(permissions.BasePermission):
    def has_permission(self, request, view):
        return request.user.is_authenticated and request.user.role == 'STAFF'

class IsCustomer(permissions.BasePermission):
    def has_permission(self, request, view):
        return request.user.is_authenticated and request.user.role == 'CUSTOMER'

class IsAppointmentOwner(permissions.BasePermission):
    def has_object_permission(self, request, view, obj):
        return obj.customer == request.user

class IsSalonStaff(permissions.BasePermission):
    def has_object_permission(self, request, view, obj):
        return (
            obj.time_slot.salon.managed_salons.filter(
                manager=request.user
            ).exists() or
            obj.staff == request.user
        )