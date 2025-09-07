# django files
from django.urls import path, include

# rest files
from rest_framework.routers import DefaultRouter

# your files
from .views import ServiceViewSet, AppointmentViewSet

app_name = 'appointments'

router = DefaultRouter()
router.register(r'services', ServiceViewSet)
router.register(r'appointments', AppointmentViewSet)

urlpatterns = [
    path('', include(router.urls)),
]