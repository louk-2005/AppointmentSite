from rest_framework import serializers
from datetime import datetime, timedelta
import jdatetime
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
    day_jalali = serializers.CharField(source='get_day_of_week_jalali', read_only=True)

    class Meta:
        model = WorkingHours
        fields = ['id', 'salon', 'day_of_week', 'day_display', 'day_jalali', 'start_time', 'end_time', 'is_active']
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
    date_jalali = serializers.SerializerMethodField()
    day_of_week_jalali = serializers.SerializerMethodField()

    class Meta:
        model = TimeSlot
        fields = [
            'id', 'salon', 'salon_name', 'date', 'date_jalali', 'start_time', 'end_time',
            'max_capacity', 'booked_count', 'available_capacity',
            'is_active', 'is_available', 'day_of_week_jalali'
        ]
        extra_kwargs = {
            'salon': {'write_only': True}
        }

    def get_date_jalali(self, obj):
        return obj.get_date_jalali()

    def get_day_of_week_jalali(self, obj):
        return obj.get_day_of_week_jalali()


class BlockedTimeSerializer(serializers.ModelSerializer):
    salon_name = serializers.CharField(source='salon.name', read_only=True)
    start_datetime_jalali = serializers.SerializerMethodField()
    end_datetime_jalali = serializers.SerializerMethodField()
    created_at_jalali = serializers.SerializerMethodField()

    class Meta:
        model = BlockedTime
        fields = [
            'id', 'salon', 'salon_name', 'start_datetime', 'start_datetime_jalali',
            'end_datetime', 'end_datetime_jalali', 'reason', 'created_at', 'created_at_jalali'
        ]
        extra_kwargs = {
            'salon': {'write_only': True}
        }

    def get_start_datetime_jalali(self, obj):
        return obj.get_start_datetime_jalali()

    def get_end_datetime_jalali(self, obj):
        return obj.get_end_datetime_jalali()

    def get_created_at_jalali(self, obj):
        return obj.get_created_at_jalali()


class TimeSlotBlockSerializer(serializers.ModelSerializer):
    time_slot_info = serializers.SerializerMethodField()
    created_at_jalali = serializers.SerializerMethodField()

    class Meta:
        model = TimeSlotBlock
        fields = ['id', 'time_slot', 'time_slot_info', 'reason', 'created_at', 'created_at_jalali']
        extra_kwargs = {
            'time_slot': {'write_only': True}
        }

    def get_time_slot_info(self, obj):
        return f"{obj.time_slot.salon.name} - {obj.time_slot.get_date_jalali()} {obj.time_slot.start_time}"

    def get_created_at_jalali(self, obj):
        return obj.get_created_at_jalali()


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