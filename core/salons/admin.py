# django files
from django.contrib import admin
from django.utils.html import format_html
from django.urls import reverse
from django.utils.safestring import mark_safe

#your files
from .models import Salon, WorkingHours, TimeSlotConfig, TimeSlot, BlockedTime, TimeSlotBlock


@admin.register(Salon)
class SalonAdmin(admin.ModelAdmin):
    list_display = ('name', 'manager', 'address_preview', 'view_time_slots_link', 'view_blocked_times_link')
    list_filter = ('manager',)
    search_fields = ('name', 'address')
    readonly_fields = ('view_time_slots_link', 'view_blocked_times_link')

    def address_preview(self, obj):
        return obj.address[:50] + '...' if len(obj.address) > 50 else obj.address

    address_preview.short_description = "آدرس"

    def view_time_slots_link(self, obj):
        count = obj.time_slots.count()
        url = reverse('admin:salons_timeslot_changelist') + f'?salon__id__exact={obj.id}'
        return format_html('<a href="{}">مشاهده تایم اسلات‌ها ({})</a>', url, count)

    view_time_slots_link.short_description = "تایم اسلات‌ها"

    def view_blocked_times_link(self, obj):
        count = obj.blocked_times.count()
        url = reverse('admin:salons_blockedtime_changelist') + f'?salon__id__exact={obj.id}'
        return format_html('<a href="{}">مشاهده زمان‌های مسدود ({})</a>', url, count)

    view_blocked_times_link.short_description = "زمان‌های مسدود"


class WorkingHoursInline(admin.TabularInline):
    model = WorkingHours
    extra = 1
    min_num = 1


class TimeSlotConfigInline(admin.StackedInline):
    model = TimeSlotConfig
    can_delete = False
    min_num = 1
    max_num = 1


class SalonAdminWithInlines(SalonAdmin):
    inlines = [WorkingHoursInline, TimeSlotConfigInline]


@admin.register(WorkingHours)
class WorkingHoursAdmin(admin.ModelAdmin):
    list_display = ('salon', 'day_of_week', 'start_time', 'end_time', 'is_active')
    list_filter = ('salon', 'day_of_week', 'is_active')
    search_fields = ('salon__name',)
    list_editable = ('start_time', 'end_time', 'is_active')


@admin.register(TimeSlotConfig)
class TimeSlotConfigAdmin(admin.ModelAdmin):
    list_display = ('salon', 'interval_minutes', 'capacity_per_slot')
    list_filter = ('salon',)
    search_fields = ('salon__name',)


@admin.register(TimeSlot)
class TimeSlotAdmin(admin.ModelAdmin):
    list_display = (
    'salon', 'date', 'start_time', 'end_time', 'max_capacity', 'booked_count', 'available_capacity', 'is_active',
    'view_appointments_link')
    list_filter = ('salon', 'date', 'is_active')
    search_fields = ('salon__name', 'date')
    readonly_fields = ('available_capacity', 'view_appointments_link')
    date_hierarchy = 'date'

    def available_capacity(self, obj):
        return obj.available_capacity

    available_capacity.short_description = "ظرفیت باقی‌مانده"

    def view_appointments_link(self, obj):
        count = obj.appointments.count()
        if count == 0:
            return "بدون رزرو"
        url = reverse('admin:appointments_appointment_changelist') + f'?time_slot__id__exact={obj.id}'
        return format_html('<a href="{}">مشاهده رزروها ({})</a>', url, count)

    view_appointments_link.short_description = "رزروها"

    actions = ['block_selected_slots', 'unblock_selected_slots']

    def block_selected_slots(self, request, queryset):
        updated = 0
        for slot in queryset:
            if slot.is_active:
                slot.block_time_slot("مسدودی دسته‌جمعی از ادمین")
                updated += 1
        self.message_user(request, f"{updated} تایم اسلات با موفقیت مسدود شدند.")

    block_selected_slots.short_description = "مسدود کردن تایم اسلات‌های انتخاب شده"

    def unblock_selected_slots(self, request, queryset):
        updated = 0
        for slot in queryset:
            if not slot.is_active:
                slot.unblock_time_slot()
                updated += 1
        self.message_user(request, f"{updated} تایم اسلات با موفقیت فعال شدند.")

    unblock_selected_slots.short_description = "فعال کردن تایم اسلات‌های انتخاب شده"


@admin.register(BlockedTime)
class BlockedTimeAdmin(admin.ModelAdmin):
    list_display = ('salon', 'start_datetime', 'end_datetime', 'reason', 'created_at', 'view_affected_slots_link')
    list_filter = ('salon', 'created_at')
    search_fields = ('salon__name', 'reason')
    readonly_fields = ('created_at', 'view_affected_slots_link')
    date_hierarchy = 'start_datetime'

    def view_affected_slots_link(self, obj):
        count = TimeSlot.objects.filter(
            salon=obj.salon,
            date=obj.start_datetime.date(),
            start_time__gte=obj.start_datetime.time(),
            start_time__lt=obj.end_datetime.time()
        ).count()
        if count == 0:
            return "بدون تایم اسلات تحت تأثیر"
        url = reverse(
            'admin:salons_timeslot_changelist') + f'?salon__id__exact={obj.salon.id}&date__exact={obj.start_datetime.date()}'
        return format_html('<a href="{}">مشاهده تایم اسلات‌ها ({})</a>', url, count)

    view_affected_slots_link.short_description = "تایم اسلات‌های تحت تأثیر"

    actions = ['unblock_selected_times']

    def unblock_selected_times(self, request, queryset):
        for blocked_time in queryset:
            blocked_time.salon.unblock_time_range(
                blocked_time.start_datetime,
                blocked_time.end_datetime
            )
        count = queryset.count()
        self.message_user(request, f"{count} بازه زمانی با موفقیت فعال شدند.")

    unblock_selected_times.short_description = "فعال کردن بازه‌های زمانی انتخاب شده"


@admin.register(TimeSlotBlock)
class TimeSlotBlockAdmin(admin.ModelAdmin):
    list_display = ('time_slot_info', 'reason', 'created_at')
    list_filter = ('time_slot__salon', 'created_at')
    search_fields = ('time_slot__salon__name', 'reason')
    readonly_fields = ('time_slot_info', 'created_at')
    date_hierarchy = 'created_at'

    def time_slot_info(self, obj):
        return f"{obj.time_slot.salon.name} - {obj.time_slot.date} {obj.time_slot.start_time}"

    time_slot_info.short_description = "تایم اسلات"

    def has_add_permission(self, request):
        return False

    def has_change_permission(self, request, obj=None):
        return False