# django files
from django.db import models
from django.core.exceptions import ValidationError

# your files
from accounts.models import User

# package files
from datetime import datetime, timedelta


class Salon(models.Model):
    name = models.CharField(max_length=100, verbose_name="نام آرایشگاه")
    address = models.TextField(verbose_name="آدرس")
    manager = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='managed_salons',
        limit_choices_to={'role': 'MANAGER'}
    )
    description = models.TextField(blank=True, verbose_name="توضیحات")

    def __str__(self):
        return self.name

    # salons/models.py (ادامه مدل Salon)

    def generate_time_slots(self, start_date, end_date):
        """
        ایجاد بازه‌های زمانی برای یک بازه تاریخ مشخص
        """
        config = self.time_slot_config
        working_hours = {wh.day_of_week: wh for wh in self.working_hours.filter(is_active=True)}
        blocked_times = self.blocked_times.filter(
            start_datetime__date__gte=start_date,
            end_datetime__date__lte=end_date
        )

        current_date = start_date
        while current_date <= end_date:
            day_of_week = current_date.weekday()

            if day_of_week in working_hours:
                wh = working_hours[day_of_week]
                start_datetime = datetime.combine(current_date, wh.start_time)
                end_datetime = datetime.combine(current_date, wh.end_time)

                current_slot_start = start_datetime
                while current_slot_start < end_datetime:
                    current_slot_end = current_slot_start + timedelta(minutes=config.interval_minutes)

                    if current_slot_end > end_datetime:
                        break

                    # بررسی اینکه آیا این تایم در بازه مسدودی قرار دارد یا خیر
                    is_blocked = any(
                        blocked.start_datetime <= current_slot_start < blocked.end_datetime
                        for blocked in blocked_times
                    )

                    TimeSlot.objects.update_or_create(
                        salon=self,
                        date=current_date,
                        start_time=current_slot_start.time(),
                        defaults={
                            'end_time': current_slot_end.time(),
                            'max_capacity': config.capacity_per_slot,
                            'is_active': not is_blocked
                        }
                    )

                    current_slot_start = current_slot_end

            current_date += timedelta(days=1)

    def block_time_range(self, start_datetime, end_datetime, reason=""):
        """
        مسدود کردن یک بازه زمانی خاص
        """
        BlockedTime.objects.create(
            salon=self,
            start_datetime=start_datetime,
            end_datetime=end_datetime,
            reason=reason
        )

        # غیرفعال کردن تایم اسلات‌هایAffected
        affected_slots = self.time_slots.filter(
            date=start_datetime.date(),
            start_time__gte=start_datetime.time(),
            start_time__lt=end_datetime.time(),
            is_active=True
        )

        for slot in affected_slots:
            slot.is_active = False
            slot.save()
            TimeSlotBlock.objects.create(time_slot=slot, reason=reason)

    def unblock_time_range(self, start_datetime, end_datetime):
        """
        رفع مسدودی یک بازه زمانی
        """
        # حذف رکوردهای مسدودی
        BlockedTime.objects.filter(
            salon=self,
            start_datetime=start_datetime,
            end_datetime=end_datetime
        ).delete()

        # فعال کردن تایم اسلات‌ها در این بازه
        affected_slots = self.time_slots.filter(
            date=start_datetime.date(),
            start_time__gte=start_datetime.time(),
            start_time__lt=end_datetime.time(),
            is_active=False
        )

        for slot in affected_slots:
            slot.blocks.all().delete()
            slot.is_active = True
            slot.save()


class WorkingHours(models.Model):
    DAY_CHOICES = [
        (0, 'شنبه'),
        (1, 'یکشنبه'),
        (2, 'دوشنبه'),
        (3, 'سه‌شنبه'),
        (4, 'چهارشنبه'),
        (5, 'پنج‌شنبه'),
        (6, 'جمعه'),
    ]

    salon = models.ForeignKey(
        Salon,
        on_delete=models.CASCADE,
        related_name='working_hours'
    )
    day_of_week = models.IntegerField(choices=DAY_CHOICES, verbose_name="روز هفته")
    start_time = models.TimeField(verbose_name="ساعت شروع")
    end_time = models.TimeField(verbose_name="ساعت پایان")
    is_active = models.BooleanField(default=True, verbose_name="فعال")

    class Meta:
        unique_together = ('salon', 'day_of_week')

    def __str__(self):
        return f"{self.salon.name} - {self.get_day_of_week_display()}"


class TimeSlotConfig(models.Model):
    salon = models.OneToOneField(
        Salon,
        on_delete=models.CASCADE,
        related_name='time_slot_config'
    )
    interval_minutes = models.PositiveIntegerField(
        default=60,
        verbose_name="فاصله زمانی بین نوبت‌ها (دقیقه)"
    )
    capacity_per_slot = models.PositiveIntegerField(
        default=3,
        verbose_name="ظرفیت هر بازه زمانی"
    )

    def __str__(self):
        return f"تنظیمات نوبت‌دهی {self.salon.name}"


class TimeSlot(models.Model):
    salon = models.ForeignKey(
        Salon,
        on_delete=models.CASCADE,
        related_name='time_slots'
    )
    date = models.DateField(verbose_name="تاریخ")
    start_time = models.TimeField(verbose_name="ساعت شروع")
    end_time = models.TimeField(verbose_name="ساعت پایان")
    max_capacity = models.PositiveIntegerField(verbose_name="ظرفیت کل")
    booked_count = models.PositiveIntegerField(default=0, verbose_name="تعداد رزرو شده")
    is_active = models.BooleanField(default=True, verbose_name="فعال")

    class Meta:
        unique_together = ('salon', 'date', 'start_time')

    def clean(self):
        super().clean()
        if self.start_time and self.end_time:
            if self.end_time <= self.start_time:
                raise ValidationError("زمان پایان باید بعد از زمان شروع باشد.")

    def __str__(self):
        return f"{self.salon.name} - {self.date} {self.start_time}"

    @property
    def available_capacity(self):
        capacity = self.max_capacity or 0
        booked = self.booked_count or 0
        return capacity - booked

    def is_available(self):
        return self.is_active and self.available_capacity > 0

    # salons/models.py (ادامه مدل TimeSlot)

    def block_time_slot(self, reason=""):
        """
        مسدود کردن یک تایم اسلات خاص
        """
        if not self.is_active:
            return False

        self.is_active = False
        self.save()

        TimeSlotBlock.objects.create(
            time_slot=self,
            reason=reason
        )
        return True

    def unblock_time_slot(self):
        """
        رفع مسدودی یک تایم اسلات
        """
        if self.is_active:
            return False

        self.blocks.all().delete()
        self.is_active = True
        self.save()
        return True


class BlockedTime(models.Model):
    salon = models.ForeignKey(
        Salon,
        on_delete=models.CASCADE,
        related_name='blocked_times'
    )
    start_datetime = models.DateTimeField(verbose_name="شروع زمان مسدود")
    end_datetime = models.DateTimeField(verbose_name="پایان زمان مسدود")
    reason = models.CharField(max_length=255, blank=True, verbose_name="دلیل مسدودی")
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = "زمان مسدود شده"
        verbose_name_plural = "زمان‌های مسدود شده"

    def __str__(self):
        return f"{self.salon.name}: {self.start_datetime} تا {self.end_datetime}"

    def clean(self):
        if self.start_datetime >= self.end_datetime:
            raise ValidationError("زمان شروع باید قبل از زمان پایان باشد")


class TimeSlotBlock(models.Model):
    time_slot = models.ForeignKey(
        TimeSlot,
        on_delete=models.CASCADE,
        related_name='blocks'
    )
    reason = models.CharField(max_length=255, blank=True, verbose_name="دلیل مسدودی")
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = "مسدودی تایم اسلات"
        verbose_name_plural = "مسدودی‌های تایم اسلات"

    def __str__(self):
        return f"{self.time_slot} - {self.reason}"
