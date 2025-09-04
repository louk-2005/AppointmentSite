# django files
from django.urls import path, include

# rest files
from rest_framework.routers import DefaultRouter

#your files
from .views import (
    SalonViewSet, WorkingHoursViewSet, TimeSlotConfigViewSet,
    TimeSlotViewSet, BlockedTimeViewSet, TimeSlotBlockViewSet
)

app_name = 'salons'

router = DefaultRouter()
router.register(r'salons', SalonViewSet)
router.register(r'working-hours', WorkingHoursViewSet)
router.register(r'time-slot-configs', TimeSlotConfigViewSet)
router.register(r'time-slots', TimeSlotViewSet)
router.register(r'blocked-times', BlockedTimeViewSet)
router.register(r'time-slot-blocks', TimeSlotBlockViewSet)

urlpatterns = [
    path('', include(router.urls)),
]