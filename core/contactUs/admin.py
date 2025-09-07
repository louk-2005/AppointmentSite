# admin.py
from django.contrib import admin
from django.utils.html import format_html
from django.urls import reverse
from .models import ContactInfo, SocialLink, Honors, License


class SocialLinkInline(admin.TabularInline):
    model = SocialLink
    extra = 1
    fields = ('name', 'url', 'icon_preview', 'icon')
    readonly_fields = ('icon_preview',)

    def icon_preview(self, obj):
        if obj.icon:
            return format_html('<img src="{}" width="50" height="50" style="object-fit: cover;" />', obj.icon.url)
        return "بدون آیکون"

    icon_preview.short_description = "پیش‌نمایش آیکون"


@admin.register(ContactInfo)
class ContactInfoAdmin(admin.ModelAdmin):
    list_display = ('name', 'phone', 'email', 'address_preview', 'updated_at', 'social_links_count')
    list_filter = ('name',)
    search_fields = ('phone', 'email', 'address')
    readonly_fields = ('logo_preview', 'updated_at', 'social_links_count')
    fieldsets = (
        ('اطلاعات اصلی', {
            'fields': ('name', 'logo', 'logo_preview')
        }),
        ('اطلاعات تماس', {
            'fields': ('description', 'phone', 'email', 'address')
        }),
    )
    inlines = [SocialLinkInline]

    def address_preview(self, obj):
        return obj.address[:50] + '...' if len(obj.address) > 50 else obj.address

    address_preview.short_description = "آدرس"

    def logo_preview(self, obj):
        if obj.logo:
            return format_html('<img src="{}" width="100" height="100" style="object-fit: cover;" />', obj.logo.url)
        return "بدون لوگو"

    logo_preview.short_description = "پیش‌نمایش لوگو"

    def social_links_count(self, obj):
        count = obj.social_links.count()
        url = reverse('admin:contactUs_sociallink_changelist') + f'?contact__id__exact={obj.id}'
        return format_html('<a href="{}">{} لینک</a>', url, count)

    social_links_count.short_description = "شبکه‌های اجتماعی"


@admin.register(SocialLink)
class SocialLinkAdmin(admin.ModelAdmin):
    list_display = ('name', 'url', 'icon_preview', 'contact')
    list_filter = ('contact',)
    search_fields = ('name', 'url')
    readonly_fields = ('icon_preview',)

    def icon_preview(self, obj):
        if obj.icon:
            return format_html('<img src="{}" width="50" height="50" style="object-fit: cover;" />', obj.icon.url)
        return "بدون آیکون"

    icon_preview.short_description = "پیش‌نمایش آیکون"


@admin.register(Honors)
class HonorsAdmin(admin.ModelAdmin):
    list_display = ('name', 'image_preview')
    search_fields = ('name',)
    readonly_fields = ('image_preview',)

    def image_preview(self, obj):
        if obj.image:
            return format_html('<img src="{}" width="150" height="100" style="object-fit: cover;" />', obj.image.url)
        return "بدون تصویر"

    image_preview.short_description = "پیش‌نمایش تصویر"

    def get_queryset(self, request):
        return super().get_queryset(request)


@admin.register(License)
class LicenseAdmin(admin.ModelAdmin):
    list_display = ('name', 'image_preview')
    search_fields = ('name',)
    readonly_fields = ('image_preview',)

    def image_preview(self, obj):
        if obj.image:
            return format_html('<img src="{}" width="100" height="150" style="object-fit: cover;" />', obj.image.url)
        return "بدون تصویر"

    image_preview.short_description = "پیش‌نمایش تصویر"

    def get_queryset(self, request):
        return super().get_queryset(request)