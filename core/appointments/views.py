# rest files
from rest_framework import viewsets, status, filters
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated, AllowAny

# django files
from django_filters.rest_framework import DjangoFilterBackend

# your files
from .models import Service, Appointment
from .serializers import (
    ServiceSerializer,
    AppointmentCreateSerializer,
    AppointmentDetailSerializer,
    AppointmentListSerializer,
    AppointmentUpdateSerializer
)
from .permissions import (
    IsSalonManager, IsStaffMember, IsCustomer,
    IsAppointmentOwner, IsSalonStaff
)


class ServiceViewSet(viewsets.ModelViewSet):
    queryset = Service.objects.all()
    serializer_class = ServiceSerializer
    permission_classes = [ AllowAny]
    filter_backends = [DjangoFilterBackend, filters.SearchFilter]
    filterset_fields = ['salon']
    search_fields = ['name', 'description']

    # def get_queryset(self):
    #     # مدیر فقط می‌تواند خدمات آرایشگاه خود را ببیند
    #     return Service.objects.filter(
    #         salon__managed_salons__manager=self.request.user
    #     )

    def perform_create(self, serializer):
        # تنظیم خودکار آرایشگاه بر اساس مدیر
        salon = self.request.user.managed_salons.first()
        serializer.save(salon=salon)


class AppointmentViewSet(viewsets.ModelViewSet):
    queryset = Appointment.objects.all()
    permission_classes = [IsAuthenticated]
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = [
        'status', 'time_slot__salon', 'time_slot__date',
        'service', 'staff'
    ]
    search_fields = [
        'customer__username', 'customer__email',
        'notes', 'time_slot__salon__name'
    ]
    ordering_fields = ['created_at', 'time_slot__date', 'time_slot__start_time']
    ordering = ['-created_at']

    def get_serializer_class(self):
        if self.action == 'create':
            return AppointmentCreateSerializer
        elif self.action == 'update' or self.action == 'partial_update':
            return AppointmentUpdateSerializer
        elif self.action == 'retrieve':
            return AppointmentDetailSerializer
        return AppointmentListSerializer

    def get_permissions(self):
        if self.action == 'create':
            self.permission_classes = [IsAuthenticated, IsCustomer]
        elif self.action in ['update', 'partial_update', 'destroy']:
            self.permission_classes = [IsAuthenticated, IsSalonStaff]
        elif self.action == 'retrieve':
            self.permission_classes = [IsAuthenticated, (IsAppointmentOwner | IsSalonStaff)]
        elif self.action == 'list':
            self.permission_classes = [IsAuthenticated]
        return super().get_permissions()

    def get_queryset(self):
        user = self.request.user
        queryset = super().get_queryset()

        # مشتری فقط رزروهای خود را می‌بیند
        if user.role == 'CUSTOMER':
            return queryset.filter(customer=user)

        # کارمند فقط رزروهای اختصاص داده شده به خود را می‌بیند
        elif user.role == 'STAFF':
            return queryset.filter(staff=user)

        # مدیر همه رزروهای آرایشگاه خود را می‌بیند
        elif user.role == 'MANAGER':
            return queryset.filter(time_slot__salon__managed_salons__manager=user)

        return queryset

    @action(detail=True, methods=['post'])
    def confirm(self, request, pk=None):
        appointment = self.get_object()
        if appointment.status != 'PENDING':
            return Response(
                {"error": "فقط رزروهای در انتظار تأیید قابل تأیید هستند"},
                status=status.HTTP_400_BAD_REQUEST
            )

        appointment.status = 'CONFIRMED'
        appointment.save()
        serializer = self.get_serializer(appointment)
        return Response(serializer.data)

    @action(detail=True, methods=['post'])
    def cancel(self, request, pk=None):
        appointment = self.get_object()
        if appointment.status in ['CANCELLED', 'COMPLETED']:
            return Response(
                {"error": "این رزرو قابل لغو نیست"},
                status=status.HTTP_400_BAD_REQUEST
            )

        # کاهش شمارنده رزروهای تایم اسلات
        appointment.time_slot.booked_count -= 1
        appointment.time_slot.save()

        appointment.status = 'CANCELLED'
        appointment.save()
        serializer = self.get_serializer(appointment)
        return Response(serializer.data)

    @action(detail=True, methods=['post'])
    def complete(self, request, pk=None):
        appointment = self.get_object()
        if appointment.status != 'CONFIRMED':
            return Response(
                {"error": "فقط رزروهای تأیید شده قابل تکمیل هستند"},
                status=status.HTTP_400_BAD_REQUEST
            )

        appointment.status = 'COMPLETED'
        appointment.save()
        serializer = self.get_serializer(appointment)
        return Response(serializer.data)

    @action(detail=False, methods=['get'])
    def my_appointments(self, request):
        """رزروهای کاربر فعلی"""
        queryset = self.get_queryset()
        serializer = self.get_serializer(queryset, many=True)
        return Response(serializer.data)

    @action(detail=False, methods=['get'])
    def available_slots(self, request):
        """تایم اسلات‌های موجود برای رزرو"""
        salon_id = request.query_params.get('salon_id')
        date = request.query_params.get('date')

        if not salon_id or not date:
            return Response(
                {"error": "salon_id و date الزامی هستند"},
                status=status.HTTP_400_BAD_REQUEST
            )

        from salons.models import TimeSlot
        from datetime import datetime

        try:
            date_obj = datetime.strptime(date, '%Y-%m-%d').date()
        except ValueError:
            return Response(
                {"error": "فرمت تاریخ نامعتبر است"},
                status=status.HTTP_400_BAD_REQUEST
            )

        slots = TimeSlot.objects.filter(
            salon_id=salon_id,
            date=date_obj,
            is_active=True
        ).filter(available_capacity__gt=0)

        from salons.serializers import TimeSlotSerializer
        serializer = TimeSlotSerializer(slots, many=True)
        return Response(serializer.data)