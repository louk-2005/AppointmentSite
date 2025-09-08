# admin.py
from django.contrib import admin
from django.utils.html import format_html
from django.urls import reverse
from .models import ContactInfo, SocialLink, Honors, License, Location, CommunicationWithUs

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

admin.site.register(Location)





@admin.register(CommunicationWithUs)
class CommunicationWithUsAdmin(admin.ModelAdmin):
    # فیلدهایی که در لیست نمایش داده می‌شوند
    list_display = ('full_name', 'email', 'phone', 'message_preview', 'is_read_status', 'created_at')

    # فیلدهای قابل جستجو
    search_fields = ('full_name', 'email', 'phone', 'message')

    # فیلترهای سمت راست صفحه
    list_filter = ('created_at', 'phone', 'is_read')

    # مرتب‌سازی پیش‌فرض
    ordering = ('-created_at',)

    # تعداد آیتم‌ها در هر صفحه
    list_per_page = 25

    # فیلدهای فقط خواندنی
    readonly_fields = ('created_at',)

    # سفارشی‌سازی ستون‌ها
    def message_preview(self, obj):
        """نمایش پیش‌نمایش پیام با محدودیت کاراکتر"""
        if len(obj.message) > 50:
            return f"{obj.message[:50]}..."
        return obj.message

    message_preview.short_description = 'پیام'

    def created_at(self, obj):
        """نمایش تاریخ ایجاد به صورت فارسی"""
        if hasattr(obj, 'created_at') and obj.created_at:
            return obj.created_at.strftime("%Y/%m/%d %H:%M")
        return "-"

    created_at.short_description = 'تاریخ ثبت'

    def phone(self, obj):
        """قالب‌بندی شماره تلفن"""
        if obj.phone:
            return format_html(
                '<span style="direction: ltr; display: inline-block;">{}</span>',
                obj.phone
            )
        return "-"

    phone.short_description = 'تلفن'

    def is_read_status(self, obj):
        """نمایش وضعیت خوانده شده با آیکون"""
        if obj.is_read:
            return format_html(
                '<span style="color: green;"><i class="fas fa-check-circle"></i> خوانده شده</span>'
            )
        return format_html(
            '<span style="color: red;"><i class="fas fa-times-circle"></i> خوانده نشده</span>'
        )

    is_read_status.short_description = 'وضعیت'
    is_read_status.admin_order_field = 'is_read'

    # سفارشی‌سازی هدر ادمین
    def changelist_view(self, request, extra_context=None):
        extra_context = extra_context or {}
        extra_context['title'] = "مدیریت پیام‌های کاربران"
        return super().changelist_view(request, extra_context=extra_context)

    # سفارشی‌سازی فرم ویرایش
    def get_form(self, request, obj=None, **kwargs):
        form = super().get_form(request, obj, **kwargs)
        form.base_fields['full_name'].label = "نام کامل"
        form.base_fields['email'].label = "ایمیل"
        form.base_fields['phone'].label = "شماره تلفن"

        # بررسی وجود فیلد message قبل از تغییر برچسب
        if 'message' in form.base_fields:
            form.base_fields['message'].label = "متن پیام"

        # تغییر برچسب فیلد is_read
        if 'is_read' in form.base_fields:
            form.base_fields['is_read'].label = "وضعیت خوانده شده"

        return form

    # اضافه کردن دکمه‌های عملیات انبوه
    actions = ['mark_as_read', 'mark_as_unread', 'export_to_excel']

    def mark_as_read(self, request, queryset):
        """علامت‌گذاری پیام‌ها به عنوان خوانده شده"""
        updated = queryset.update(is_read=True)
        self.message_user(
            request,
            f"{updated} پیام به عنوان خوانده شده علامت‌گذاری شدند.",
            'success'
        )

    mark_as_read.short_description = "علامت‌گذاری به عنوان خوانده شده"

    def mark_as_unread(self, request, queryset):
        """علامت‌گذاری پیام‌ها به عنوان خوانده نشده"""
        updated = queryset.update(is_read=False)
        self.message_user(
            request,
            f"{updated} پیام به عنوان خوانده نشده علامت‌گذاری شدند.",
            'success'
        )

    mark_as_unread.short_description = "علامت‌گذاری به عنوان خوانده نشده"

    def export_to_excel(self, request, queryset):
        """خروجی Excel از پیام‌های انتخاب شده"""
        try:
            from openpyxl import Workbook
            from openpyxl.styles import Font, Alignment, PatternFill, Border, Side
            from openpyxl.utils import get_column_letter
            from django.http import HttpResponse
        except ImportError:
            self.message_user(request, "برای خروجی اکسل باید کتابخانه openpyxl نصب شود: pip install openpyxl", 'error')
            return

        # ایجاد یک Workbook جدید
        wb = Workbook()
        ws = wb.active
        ws.title = "پیام‌های کاربران"

        # تعریف استایل‌ها
        header_font = Font(name='Arial', bold=True, size=12, color='FFFFFF')
        header_fill = PatternFill(start_color='4F81BD', end_color='4F81BD', fill_type='solid')
        header_alignment = Alignment(horizontal='center', vertical='center', wrap_text=True)

        # تعریف حاشیه‌ها
        thin_border = Border(
            left=Side(style='thin'),
            right=Side(style='thin'),
            top=Side(style='thin'),
            bottom=Side(style='thin')
        )

        # نوشتن هدر جدول
        headers = ['نام کامل', 'ایمیل', 'شماره تلفن', 'متن پیام', 'وضعیت خوانده شده', 'تاریخ ثبت']
        for col_num, header in enumerate(headers, 1):
            cell = ws.cell(row=1, column=col_num)
            cell.value = header
            cell.font = header_font
            cell.fill = header_fill
            cell.alignment = header_alignment
            cell.border = thin_border

        # نوشتن داده‌ها
        for row_num, message in enumerate(queryset, 2):
            # نام کامل
            cell = ws.cell(row=row_num, column=1, value=message.full_name)
            cell.border = thin_border

            # ایمیل
            cell = ws.cell(row=row_num, column=2, value=message.email)
            cell.border = thin_border

            # شماره تلفن
            cell = ws.cell(row=row_num, column=3, value=message.phone or "")
            cell.border = thin_border

            # متن پیام
            cell = ws.cell(row=row_num, column=4, value=message.message)
            cell.border = thin_border
            cell.alignment = Alignment(horizontal='left', vertical='top', wrap_text=True)

            # وضعیت خوانده شده
            status = "خوانده شده" if message.is_read else "خوانده نشده"
            cell = ws.cell(row=row_num, column=5, value=status)
            cell.border = thin_border
            cell.alignment = Alignment(horizontal='center')

            # تاریخ ثبت
            date_value = message.created_at.strftime("%Y/%m/%d %H:%M") if message.created_at else ""
            cell = ws.cell(row=row_num, column=6, value=date_value)
            cell.border = thin_border
            cell.alignment = Alignment(horizontal='center')

        # تنظیم عرض ستون‌ها
        column_widths = [20, 25, 15, 50, 20, 20]
        for i, width in enumerate(column_widths, 1):
            ws.column_dimensions[get_column_letter(i)].width = width

        # تنظیم ارتفاع ردیف هدر
        ws.row_dimensions[1].height = 25

        # ایجاد پاسخ HTTP
        response = HttpResponse(
            content_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
        )
        response['Content-Disposition'] = 'attachment; filename="messages.xlsx"'

        # ذخیره Workbook در پاسخ
        wb.save(response)

        return response

    export_to_excel.short_description = "خروجی Excel از پیام‌ها"


    # سفارشی‌سازی نمایش جزئیات
    fieldsets = (
        ('اطلاعات کاربر', {
            'fields': ('full_name', 'email', 'phone')
        }),
        ('محتوای پیام', {
            'fields': ('message',),
            'classes': ('wide',),
            'description': 'متن کامل پیام ارسالی توسط کاربر'
        }),
        ('وضعیت پیام', {
            'fields': ('is_read',),
            'classes': ('collapse',),
            'description': 'وضعیت خوانده شدن پیام توسط ادمین'
        }),
        ('اطلاعات سیستمی', {
            'fields': ('created_at',),
            'classes': ('collapse',),
            'description': 'اطلاعات ثبت پیام در سیستم'
        }),
    )

    # اضافه کردن کلاس‌های CSS برای بهبود ظاهر
    class Media:
        css = {
            'all': ('https://cdnjs.cloudflare.com/ajax/libs/font-awesome/5.15.4/css/all.min.css',)
        }