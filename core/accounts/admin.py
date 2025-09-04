from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from django.utils.html import mark_safe
from .models import User


class AccountsUserAdmin(UserAdmin):
    # نمایش تصویر در لیست کاربران
    list_display = (
        'image_tag',
        'username',
        'email',
        'role',
        'first_name',
        'last_name',
        'is_active',
        'date_joined',
        'last_login'
    )

    # فیلترهای پیشرفته
    list_filter = (
        'role',
        'is_active',
        'is_staff',
        'is_superuser',
        'date_joined',
        'last_login'
    )

    # جستجوی گسترده
    search_fields = (
        'username',
        'email',
        'first_name',
        'last_name',
        'phone_number'
    )

    ordering = ('-date_joined',)
    list_per_page = 25
    readonly_fields = ('image_tag_preview',)

    # فیلدهای اصلی برای ویرایش کاربر
    fieldsets = (
        (None, {'fields': ('username', 'password')}),
        ('اطلاعات شخصی', {
            'fields': (
                'first_name',
                'last_name',
                'email',
                'phone_number',
                'role',
                'image'
            )
        }),
        ('دسترسی‌ها', {
            'fields': (
                'is_active',
                'is_staff',
                'is_superuser',
                'groups',
                'user_permissions'
            )
        }),
        ('تاریخ‌های مهم', {
            'fields': ('last_login', 'date_joined')
        }),
        ('پیش‌نمایش تصویر', {
            'fields': ('image_tag_preview',),
            'classes': ('collapse',),
        }),
    )

    # فیلدهای ایجاد کاربر جدید
    add_fieldsets = (
        (None, {
            'classes': ('wide',),
            'fields': (
                'username',
                'email',
                'phone_number',
                'role',
                'password1',
                'password2',
                'image'
            )
        }),
    )

    # اکشن‌های سفارشی
    actions = ['activate_users', 'deactivate_users']

    def activate_users(self, request, queryset):
        updated = queryset.update(is_active=True)
        self.message_user(
            request,
            f'{updated} کاربر با موفقیت فعال شدند.',
            level='success'
        )

    activate_users.short_description = "فعال‌سازی کاربران انتخاب‌شده"

    def deactivate_users(self, request, queryset):
        updated = queryset.update(is_active=False)
        self.message_user(
            request,
            f'{updated} کاربر با موفقیت غیرفعال شدند.',
            level='warning'
        )

    deactivate_users.short_description = "غیرفعال‌سازی کاربران انتخاب‌شده"

    # نمایش تصویر در لیست کاربران
    def image_tag(self, obj):
        if obj.image and obj.image.name != 'default.jpg':
            return mark_safe(
                f'<img src="{obj.image.url}" width="50" height="50" style="border-radius:50%; object-fit: cover;" />'
            )
        return mark_safe(
            '<img src="/media/default.jpg" width="50" height="50" style="border-radius:50%; object-fit: cover;" />'
        )

    image_tag.short_description = 'تصویر'
    image_tag.allow_tags = True

    # نمایش تصویر بزرگتر در فرم ویرایش
    def image_tag_preview(self, obj):
        if obj.image and obj.image.name != 'default.jpg':
            return mark_safe(
                f'<img src="{obj.image.url}" width="200" height="200" style="border-radius:10%; object-fit: cover;" />'
            )
        return mark_safe(
            '<img src="/media/default.jpg" width="200" height="200" style="border-radius:10%; object-fit: cover;" />'
        )

    image_tag_preview.short_description = 'پیش‌نمایش تصویر'
    image_tag_preview.allow_tags = True


admin.site.register(User, AccountsUserAdmin)