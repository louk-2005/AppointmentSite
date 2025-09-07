# django files
from django.urls import path, include

# rest files
from rest_framework.routers import DefaultRouter

# your files
from .views import UserViewSet, HomeImageViewSet

app_name = 'accounts'

router = DefaultRouter()
router.register('users', UserViewSet, basename='users')
router.register('home/images', HomeImageViewSet, basename='home_images')

urlpatterns = [
    path('', include(router.urls)),
]
