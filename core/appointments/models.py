# django files
from django.db import models
from django.core.exceptions import ValidationError

#your files
from accounts.models import User
from salons.models import Salon, TimeSlot


class Service(models.Model):
    salon = models.ForeignKey(
        Salon,
        on_delete=models.CASCADE,
        related_name='services'
    )
    name = models.CharField(max_length=100, verbose_name="نام خدمت")
    description = models.TextField(verbose_name="توضیحات")
    image = models.ImageField(default='service/default.png', upload_to='service', blank=True, null=True)
    duration = models.DurationField(verbose_name="مدت زمان")
    price = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        verbose_name="قیمت"
    )
    show = models.BooleanField(default=False)


    def __str__(self):
        return self.name


class Appointment(models.Model):
    STATUS_CHOICES = [
        ('PENDING', 'در انتظار تأیید'),
        ('CONFIRMED', 'تأیید شده'),
        ('CANCELLED', 'لغو شده'),
        ('COMPLETED', 'تکمیل شده'),
    ]

    customer = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='appointments',
        limit_choices_to={'role': 'CUSTOMER'}
    )
    time_slot = models.ForeignKey(
        TimeSlot,
        on_delete=models.CASCADE,
        related_name='appointments'
    )
    staff = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='staff_appointments',
        limit_choices_to={'role': 'STAFF'}
    )
    service = models.ForeignKey(
        Service,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='appointments'
    )
    status = models.CharField(
        max_length=20,
        choices=STATUS_CHOICES,
        default='PENDING',
        verbose_name="وضعیت"
    )
    notes = models.TextField(blank=True, verbose_name="یادداشت‌ها")
    created_at = models.DateTimeField(auto_now_add=True)

    def clean(self):
        if not self.time_slot.is_available():
            raise ValidationError("این بازه زمانی دیگر در دسترس نیست")

    def save(self, *args, **kwargs):
        if self.pk is None:  # فقط برای رزروهای جدید
            if self.time_slot.available_capacity <= 0:
                raise ValidationError("ظرفیت این بازه زمانی تکمیل شده است")

        super().save(*args, **kwargs)

        if self.pk is None:  # فقط برای رزروهای جدید
            self.time_slot.booked_count += 1
            self.time_slot.save()

    def __str__(self):
        return f"{self.customer.username} - {self.time_slot}"