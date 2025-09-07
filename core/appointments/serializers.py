# appointments/serializers.py
from rest_framework import serializers
from django.utils import timezone
from .models import Service, Appointment
from accounts.serializers import UserProfileSerializer
from salons.serializers import TimeSlotSerializer


class ServiceSerializer(serializers.ModelSerializer):
    salon_name = serializers.CharField(source='salon.name', read_only=True)
    duration_minutes = serializers.SerializerMethodField()

    class Meta:
        model = Service
        fields = [
            'id', 'salon', 'salon_name', 'name', 'description',
            'duration', 'duration_minutes', 'price'
        ]
        extra_kwargs = {
            'salon': {'write_only': True}
        }

    def get_duration_minutes(self, obj):
        return int(obj.duration.total_seconds() // 60)


class AppointmentCreateSerializer(serializers.ModelSerializer):
    customer = serializers.HiddenField(default=serializers.CurrentUserDefault())
    status = serializers.ChoiceField(choices=Appointment.STATUS_CHOICES, read_only=True)

    class Meta:
        model = Appointment
        fields = [
            'id', 'customer', 'time_slot', 'staff', 'service',
            'status', 'notes'
        ]

    def validate(self, data):
        # بررسی در دسترس بودن تایم اسلات
        time_slot = data.get('time_slot')
        if not time_slot.is_available():
            raise serializers.ValidationError(
                {"time_slot": "این بازه زمانی دیگر در دسترس نیست"}
            )

        # بررسی ظرفیت تایم اسلات
        if time_slot.available_capacity <= 0:
            raise serializers.ValidationError(
                {"time_slot": "ظرفیت این بازه زمانی تکمیل شده است"}
            )

        # بررسی تداخل زمانی با رزروهای دیگر مشتری
        customer = data.get('customer')
        existing_appointments = Appointment.objects.filter(
            customer=customer,
            time_slot__date=time_slot.date,
            status__in=['PENDING', 'CONFIRMED']
        ).exclude(pk=self.instance.pk if self.instance else None)

        if existing_appointments.exists():
            raise serializers.ValidationError(
                {"time_slot": "شما در این تاریخ رزرو دیگری دارید"}
            )

        return data

    def create(self, validated_data):
        appointment = super().create(validated_data)
        # به‌روزرسانی شمارنده رزروهای تایم اسلات
        appointment.time_slot.booked_count += 1
        appointment.time_slot.save()
        return appointment


class AppointmentDetailSerializer(serializers.ModelSerializer):
    customer = UserProfileSerializer(read_only=True)
    staff = UserProfileSerializer(read_only=True)
    time_slot = TimeSlotSerializer(read_only=True)
    service = ServiceSerializer(read_only=True)
    status_display = serializers.CharField(source='get_status_display', read_only=True)
    created_at = serializers.DateTimeField(read_only=True)

    class Meta:
        model = Appointment
        fields = [
            'id', 'customer', 'time_slot', 'staff', 'service',
            'status', 'status_display', 'notes', 'created_at'
        ]


class AppointmentListSerializer(serializers.ModelSerializer):
    salon_name = serializers.CharField(source='time_slot.salon.name', read_only=True)
    date = serializers.DateField(source='time_slot.date', read_only=True)
    start_time = serializers.TimeField(source='time_slot.start_time', read_only=True)
    end_time = serializers.TimeField(source='time_slot.end_time', read_only=True)
    service_name = serializers.CharField(source='service.name', read_only=True)
    customer_name = serializers.CharField(source='customer.username', read_only=True)
    staff_name = serializers.CharField(source='staff.username', read_only=True)
    status_display = serializers.CharField(source='get_status_display', read_only=True)

    class Meta:
        model = Appointment
        fields = [
            'id', 'salon_name', 'date', 'start_time', 'end_time',
            'service_name', 'customer_name', 'staff_name',
            'status', 'status_display', 'created_at'
        ]


class AppointmentUpdateSerializer(serializers.ModelSerializer):
    class Meta:
        model = Appointment
        fields = ['status', 'notes', 'staff']

    def validate_status(self, value):
        # بررسی منطق تغییر وضعیت
        if self.instance and self.instance.status == 'CANCELLED' and value != 'CANCELLED':
            raise serializers.ValidationError(
                "نمی‌توان وضعیت رزرو لغو شده را تغییر داد"
            )
        return value