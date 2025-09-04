# rest files
from rest_framework import serializers

# package files
from datetime import datetime, timedelta

# your files
from .models import Salon, WorkingHours, TimeSlotConfig, TimeSlot, BlockedTime, TimeSlotBlock


class SalonSerializer(serializers.ModelSerializer):
    manager_name = serializers.CharField(source='manager.username', read_only=True)

    class Meta:
        model = Salon
        fields = ['id', 'name', 'address', 'manager', 'manager_name', 'description']
        extra_kwargs = {
            'manager': {'write_only': True}
        }


class WorkingHoursSerializer(serializers.ModelSerializer):
    day_display = serializers.CharField(source='get_day_of_week_display', read_only=True)

    class Meta:
        model = WorkingHours
        fields = ['id', 'salon', 'day_of_week', 'day_display', 'start_time', 'end_time', 'is_active']
        extra_kwargs = {
            'salon': {'write_only': True}
        }


class TimeSlotConfigSerializer(serializers.ModelSerializer):
    class Meta:
        model = TimeSlotConfig
        fields = ['id', 'salon', 'interval_minutes', 'capacity_per_slot']
        extra_kwargs = {
            'salon': {'write_only': True}
        }


class TimeSlotSerializer(serializers.ModelSerializer):
    salon_name = serializers.CharField(source='salon.name', read_only=True)
    available_capacity = serializers.IntegerField(read_only=True)
    is_available = serializers.BooleanField(read_only=True)

    class Meta:
        model = TimeSlot
        fields = [
            'id', 'salon', 'salon_name', 'date', 'start_time', 'end_time',
            'max_capacity', 'booked_count', 'available_capacity',
            'is_active', 'is_available'
        ]
        extra_kwargs = {
            'salon': {'write_only': True}
        }


class BlockedTimeSerializer(serializers.ModelSerializer):
    salon_name = serializers.CharField(source='salon.name', read_only=True)

    class Meta:
        model = BlockedTime
        fields = [
            'id', 'salon', 'salon_name', 'start_datetime', 'end_datetime',
            'reason', 'created_at'
        ]
        extra_kwargs = {
            'salon': {'write_only': True}
        }


class TimeSlotBlockSerializer(serializers.ModelSerializer):
    time_slot_info = serializers.SerializerMethodField()

    class Meta:
        model = TimeSlotBlock
        fields = ['id', 'time_slot', 'time_slot_info', 'reason', 'created_at']
        extra_kwargs = {
            'time_slot': {'write_only': True}
        }

    def get_time_slot_info(self, obj):
        return f"{obj.time_slot.salon.name} - {obj.time_slot.date} {obj.time_slot.start_time}"


class SalonDetailSerializer(serializers.ModelSerializer):
    working_hours = WorkingHoursSerializer(source='working_hours', many=True, read_only=True)
    time_slot_config = TimeSlotConfigSerializer(read_only=True)

    class Meta:
        model = Salon
        fields = ['id', 'name', 'address', 'manager', 'description', 'working_hours', 'time_slot_config']


class TimeSlotGenerationSerializer(serializers.Serializer):
    start_date = serializers.DateField()
    end_date = serializers.DateField()

    def validate(self, data):
        if data['start_date'] > data['end_date']:
            raise serializers.ValidationError("تاریخ شروع باید قبل از تاریخ پایان باشد")
        return data


class TimeSlotBlockRangeSerializer(serializers.Serializer):
    start_datetime = serializers.DateTimeField()
    end_datetime = serializers.DateTimeField()
    reason = serializers.CharField(required=False, allow_blank=True)

    def validate(self, data):
        if data['start_datetime'] >= data['end_datetime']:
            raise serializers.ValidationError("زمان شروع باید قبل از زمان پایان باشد")
        return data


class TimeSlotUnblockRangeSerializer(serializers.Serializer):
    start_datetime = serializers.DateTimeField()
    end_datetime = serializers.DateTimeField()

    def validate(self, data):
        if data['start_datetime'] >= data['end_datetime']:
            raise serializers.ValidationError("زمان شروع باید قبل از زمان پایان باشد")
        return data