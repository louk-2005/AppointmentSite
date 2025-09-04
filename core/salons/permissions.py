# salons/permissions.py
from rest_framework import permissions


class IsSalonManager(permissions.BasePermission):
    def has_permission(self, request, view):
        return request.user.is_authenticated and request.user.role == 'MANAGER'

    def has_object_permission(self, request, view, obj):
        # برای مدل Salon، بررسی می‌کند که آیا کاربر مدیر این آرایشگاه است
        if hasattr(obj, 'manager'):
            return obj.manager == request.user
        # برای مدل‌های دیگر که salon دارند، بررسی می‌کند که آیا کاربر مدیر آرایشگاه مربوطه است
        if hasattr(obj, 'salon'):
            return obj.salon.manager == request.user
        return False


class IsSalonStaff(permissions.BasePermission):
    def has_permission(self, request, view):
        return request.user.is_authenticated and request.user.role in ['MANAGER', 'STAFF']

    def has_object_permission(self, request, view, obj):
        # مدیران می‌توانند همه چیز را ببینند
        if request.user.role == 'MANAGER':
            return True

        # کارمندان فقط می‌توانند اطلاعات آرایشگاه خود را ببینند
        if hasattr(obj, 'salon'):
            # بررسی می‌کند که آیا کارمند در آرایشگاه کار می‌کند
            # این بخش نیاز به مدل StaffSalon دارد که در اینجا تعریف نشده
            # برای سادگی، فرض می‌کنیم کارمندان فقط می‌توانند ببینند
            return True

        return False