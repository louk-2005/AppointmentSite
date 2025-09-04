# salons/views.py
from rest_framework import viewsets, status, filters
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from django_filters.rest_framework import DjangoFilterBackend
from django.utils import timezone
from .models import Salon, WorkingHours, TimeSlotConfig, TimeSlot, BlockedTime, TimeSlotBlock
from .serializers import (
    SalonSerializer, SalonDetailSerializer, WorkingHoursSerializer,
    TimeSlotConfigSerializer, TimeSlotSerializer, BlockedTimeSerializer,
    TimeSlotBlockSerializer, TimeSlotGenerationSerializer,
    TimeSlotBlockRangeSerializer, TimeSlotUnblockRangeSerializer
)
from .permissions import IsSalonManager, IsSalonStaff


class SalonViewSet(viewsets.ModelViewSet):
    queryset = Salon.objects.all()
    serializer_class = SalonSerializer
    permission_classes = [IsAuthenticated, IsSalonManager]
    filter_backends = [filters.SearchFilter]
    search_fields = ['name', 'address']

    def get_serializer_class(self):
        if self.action == 'retrieve':
            return SalonDetailSerializer
        return SalonSerializer

    def get_queryset(self):
        # مدیر فقط آرایشگاه‌های خود را می‌بیند
        return Salon.objects.filter(manager=self.request.user)

    def perform_create(self, serializer):
        serializer.save(manager=self.request.user)


class WorkingHoursViewSet(viewsets.ModelViewSet):
    queryset = WorkingHours.objects.all()
    serializer_class = WorkingHoursSerializer
    permission_classes = [IsAuthenticated, IsSalonManager]
    filter_backends = [DjangoFilterBackend, filters.SearchFilter]
    filterset_fields = ['salon', 'day_of_week', 'is_active']
    search_fields = ['salon__name']

    def get_queryset(self):
        # مدیر فقط ساعات کاری آرایشگاه خود را می‌بیند
        return WorkingHours.objects.filter(salon__manager=self.request.user)


class TimeSlotConfigViewSet(viewsets.ModelViewSet):
    queryset = TimeSlotConfig.objects.all()
    serializer_class = TimeSlotConfigSerializer
    permission_classes = [IsAuthenticated, IsSalonManager]

    def get_queryset(self):
        # مدیر فقط تنظیمات آرایشگاه خود را می‌بیند
        return TimeSlotConfig.objects.filter(salon__manager=self.request.user)


class TimeSlotViewSet(viewsets.ModelViewSet):
    queryset = TimeSlot.objects.all()
    serializer_class = TimeSlotSerializer
    permission_classes = [IsAuthenticated, IsSalonStaff]
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ['salon', 'date', 'is_active']
    search_fields = ['salon__name']
    ordering_fields = ['date', 'start_time']
    ordering = ['date', 'start_time']

    def get_queryset(self):
        user = self.request.user
        queryset = super().get_queryset()

        # مدیر همه تایم اسلات‌های آرایشگاه خود را می‌بیند
        if user.role == 'MANAGER':
            return queryset.filter(salon__manager=user)

        # کارمندان تایم اسلات‌های آرایشگاه خود را می‌بینند
        elif user.role == 'STAFF':
            # فرض می‌کنیم کارمند در یک آرایشگاه کار می‌کند
            # در عمل نیاز به مدل ارتباطی بین کارمند و آرایشگاه دارید
            return queryset.filter(salon__staff=user)

        return queryset.none()

    @action(detail=False, methods=['post'])
    def generate_slots(self, request):
        """ایجاد تایم اسلات‌ها برای یک بازه تاریخ"""
        serializer = TimeSlotGenerationSerializer(data=request.data)
        if serializer.is_valid():
            start_date = serializer.validated_data['start_date']
            end_date = serializer.validated_data['end_date']

            # دریافت آرایشگاه کاربر
            try:
                salon = request.user.managed_salons.get()
            except Salon.DoesNotExist:
                return Response(
                    {"error": "شما آرایشگاهی را مدیریت نمی‌کنید"},
                    status=status.HTTP_400_BAD_REQUEST
                )

            # ایجاد تایم اسلات‌ها
            salon.generate_time_slots(start_date, end_date)

            return Response(
                {"message": f"تایم اسلات‌ها از {start_date} تا {end_date} ایجاد شدند"},
                status=status.HTTP_200_OK
            )

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    @action(detail=True, methods=['post'])
    def block_slot(self, request, pk=None):
        """مسدود کردن یک تایم اسلات خاص"""
        time_slot = self.get_object()
        reason = request.data.get('reason', '')

        if time_slot.block_time_slot(reason):
            return Response(
                {"message": "تایم اسلات با موفقیت مسدود شد"},
                status=status.HTTP_200_OK
            )

        return Response(
            {"error": "این تایم اسلات قبلاً مسدود شده است"},
            status=status.HTTP_400_BAD_REQUEST
        )

    @action(detail=True, methods=['post'])
    def unblock_slot(self, request, pk=None):
        """رفع مسدودی یک تایم اسلات"""
        time_slot = self.get_object()

        if time_slot.unblock_time_slot():
            return Response(
                {"message": "مسدودی تایم اسلات با موفقیت رفع شد"},
                status=status.HTTP_200_OK
            )

        return Response(
            {"error": "این تایم اسلات مسدود نشده است"},
            status=status.HTTP_400_BAD_REQUEST
        )


class BlockedTimeViewSet(viewsets.ModelViewSet):
    queryset = BlockedTime.objects.all()
    serializer_class = BlockedTimeSerializer
    permission_classes = [IsAuthenticated, IsSalonManager]
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ['salon']
    search_fields = ['salon__name', 'reason']
    ordering_fields = ['start_datetime', 'created_at']
    ordering = ['-created_at']

    def get_queryset(self):
        # مدیر فقط زمان‌های مسدود شده آرایشگاه خود را می‌بیند
        return BlockedTime.objects.filter(salon__manager=self.request.user)

    @action(detail=False, methods=['post'])
    def block_time_range(self, request):
        """مسدود کردن یک بازه زمانی"""
        serializer = TimeSlotBlockRangeSerializer(data=request.data)
        if serializer.is_valid():
            start_datetime = serializer.validated_data['start_datetime']
            end_datetime = serializer.validated_data['end_datetime']
            reason = serializer.validated_data.get('reason', '')

            # دریافت آرایشگاه کاربر
            try:
                salon = request.user.managed_salons.get()
            except Salon.DoesNotExist:
                return Response(
                    {"error": "شما آرایشگاهی را مدیریت نمی‌کنید"},
                    status=status.HTTP_400_BAD_REQUEST
                )

            # مسدود کردن بازه زمانی
            salon.block_time_range(start_datetime, end_datetime, reason)

            return Response(
                {"message": f"بازه زمانی از {start_datetime} تا {end_datetime} مسدود شد"},
                status=status.HTTP_200_OK
            )

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    @action(detail=False, methods=['post'])
    def unblock_time_range(self, request):
        """رفع مسدودی یک بازه زمانی"""
        serializer = TimeSlotUnblockRangeSerializer(data=request.data)
        if serializer.is_valid():
            start_datetime = serializer.validated_data['start_datetime']
            end_datetime = serializer.validated_data['end_datetime']

            # دریافت آرایشگاه کاربر
            try:
                salon = request.user.managed_salons.get()
            except Salon.DoesNotExist:
                return Response(
                    {"error": "شما آرایشگاهی را مدیریت نمی‌کنید"},
                    status=status.HTTP_400_BAD_REQUEST
                )

            # رفع مسدودی بازه زمانی
            salon.unblock_time_range(start_datetime, end_datetime)

            return Response(
                {"message": f"مسدودی بازه زمانی از {start_datetime} تا {end_datetime} رفع شد"},
                status=status.HTTP_200_OK
            )

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class TimeSlotBlockViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = TimeSlotBlock.objects.all()
    serializer_class = TimeSlotBlockSerializer
    permission_classes = [IsAuthenticated, IsSalonStaff]
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ['time_slot__salon']
    search_fields = ['reason', 'time_slot__salon__name']
    ordering_fields = ['created_at']
    ordering = ['-created_at']

    def get_queryset(self):
        user = self.request.user
        queryset = super().get_queryset()

        # مدیر همه مسدودی‌های آرایشگاه خود را می‌بیند
        if user.role == 'MANAGER':
            return queryset.filter(time_slot__salon__manager=user)

        # کارمندان مسدودی‌های آرایشگاه خود را می‌بینند
        elif user.role == 'STAFF':
            # فرض می‌کنیم کارمند در یک آرایشگاه کار می‌کند
            return queryset.filter(time_slot__salon__staff=user)

        return queryset.none()