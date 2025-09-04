# django files
from django.urls import path, include

# rest files
from rest_framework.routers import DefaultRouter

# your files
from .views import UserViewSet

app_name = 'accounts'

router = DefaultRouter()
router.register('users', UserViewSet, basename='users')

urlpatterns = [
    path('', include(router.urls)),
]
