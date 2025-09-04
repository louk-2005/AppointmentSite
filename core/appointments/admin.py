# django files
from django.contrib import admin
from django.utils.html import format_html
from django.urls import reverse
from django.utils.safestring import mark_safe

#your files
from .models import Service, Appointment


@admin.register(Service)
class ServiceAdmin(admin.ModelAdmin):
    list_display = ('name', 'salon', 'duration', 'price', 'view_appointments_link')
    list_filter = ('salon',)
    search_fields = ('name', 'description', 'salon__name')
    list_editable = ('duration', 'price')

    def view_appointments_link(self, obj):
        count = obj.appointments.count()
        if count == 0:
            return "بدون رزرو"
        url = reverse('admin:appointments_appointment_changelist') + f'?service__id__exact={obj.id}'
        return format_html('<a href="{}">مشاهده رزروها ({})</a>', url, count)

    view_appointments_link.short_description = "رزروها"


@admin.register(Appointment)
class AppointmentAdmin(admin.ModelAdmin):
    list_display = (
    'customer_info', 'time_slot_info', 'service_info', 'staff_info', 'status', 'created_at', 'actions_buttons')
    list_filter = ('status', 'time_slot__salon', 'time_slot__date', 'service', 'staff')
    search_fields = ('customer__username', 'customer__email', 'notes', 'time_slot__salon__name')
    readonly_fields = ('created_at', 'customer_info', 'time_slot_info', 'service_info', 'staff_info')
    date_hierarchy = 'time_slot__date'

    fieldsets = (
        ('اطلاعات اصلی', {
            'fields': ('customer', 'time_slot', 'service', 'staff', 'status')
        }),
        ('جزئیات', {
            'fields': ('notes', 'created_at')
        }),
    )

    def customer_info(self, obj):
        return format_html(
            '<strong>{}</strong><br>{}<br>{}',
            obj.customer.username,
            obj.customer.email,
            obj.customer.phone_number or "شماره تلفن ثبت نشده"
        )

    customer_info.short_description = "مشتری"

    def time_slot_info(self, obj):
        return format_html(
            '<strong>{}</strong><br>{}<br>{} - {}',
            obj.time_slot.salon.name,
            obj.time_slot.date,
            obj.time_slot.start_time,
            obj.time_slot.end_time
        )

    time_slot_info.short_description = "تایم اسلات"

    def service_info(self, obj):
        if obj.service:
            return format_html(
                '<strong>{}</strong><br>{} دقیقه<br>{} تومان',
                obj.service.name,
                obj.service.duration.total_seconds() // 60,
                obj.service.price
            )
        return "خدمت انتخاب نشده"

    service_info.short_description = "خدمت"

    def staff_info(self, obj):
        if obj.staff:
            return format_html(
                '<strong>{}</strong><br>{}',
                obj.staff.username,
                obj.staff.phone_number or "شماره تلفن ثبت نشده"
            )
        return "کارمند اختصاص داده نشده"

    staff_info.short_description = "کارمند"

    def actions_buttons(self, obj):
        buttons = []

        if obj.status == 'PENDING':
            confirm_url = reverse('admin:appointments_appointment_change', args=[obj.pk])
            buttons.append(
                format_html('<a class="button" href="{}?status=CONFIRMED">تأیید</a>', confirm_url)
            )

        if obj.status in ['PENDING', 'CONFIRMED']:
            cancel_url = reverse('admin:appointments_appointment_change', args=[obj.pk])
            buttons.append(
                format_html('<a class="button" style="background-color:#f44336;" href="{}?status=CANCELLED">لغو</a>',
                            cancel_url)
            )

        if obj.status == 'CONFIRMED':
            complete_url = reverse('admin:appointments_appointment_change', args=[obj.pk])
            buttons.append(
                format_html('<a class="button" style="background-color:#4CAF50;" href="{}?status=COMPLETED">تکمیل</a>',
                            complete_url)
            )

        return mark_safe(' '.join(buttons)) if buttons else "—"

    actions_buttons.short_description = "عملیات"

    def response_change(self, request, obj):
        if '_save' in request.POST and 'status' in request.GET:
            obj.status = request.GET['status']
            obj.save()
            self.message_user(request, f"وضعیت رزرو به '{obj.get_status_display()}' تغییر یافت.")
        return super().response_change(request, obj)

    actions = ['confirm_selected', 'cancel_selected', 'complete_selected']

    def confirm_selected(self, request, queryset):
        updated = queryset.filter(status='PENDING').update(status='CONFIRMED')
        self.message_user(request, f"{updated} رزرو با موفقیت تأیید شدند.")

    confirm_selected.short_description = "تأیید رزروهای انتخاب شده"

    def cancel_selected(self, request, queryset):
        updated = queryset.exclude(status='CANCELLED').update(status='CANCELLED')
        self.message_user(request, f"{updated} رزرو با موفقیت لغو شدند.")

    cancel_selected.short_description = "لغو رزروهای انتخاب شده"

    def complete_selected(self, request, queryset):
        updated = queryset.filter(status='CONFIRMED').update(status='COMPLETED')
        self.message_user(request, f"{updated} رزرو با موفقیت تکمیل شدند.")

    complete_selected.short_description = "تکمیل رزروهای انتخاب شده"