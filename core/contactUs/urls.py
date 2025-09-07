# django files
from django.urls import path, include

# rest files
from rest_framework.routers import DefaultRouter

# your files
from . import views

app_name = 'accounts'

router = DefaultRouter()
router.register(r'contacts', views.ContactViewSet, basename='contact')
router.register(r'social/links', views.SocialLinkViewSet, basename='social-link')
router.register(r'honors', views.HonorViewSet, basename='honors')
router.register(r'licenses', views.LicenseViewSet, basename='licenses')

urlpatterns = [
    path('', include(router.urls)),
]